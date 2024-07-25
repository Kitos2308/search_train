import asyncio
import contextlib
from typing import AsyncIterator
from dynaconf import settings
from elasticsearch import AsyncElasticsearch
from loguru import logger


SEARCH_INDEX_NAME_ALPHA = "searchable-document-index-alpha"
SEARCH_INDEX_NAME_BETA = "searchable-document-index-beta"
ACTIVE_SEARCH_INDEX_ALIAS = "searchable-document-index-alias"

class IndexManager:
    def __init__(self, elasticsearch_connection: AsyncElasticsearch):
        self.elasticsearch_connection = elasticsearch_connection
        self._active_index_cache: str | None = None
        self._inactive_index_cache: str | None = None

    async def get_active_write_index_name(self) -> str:
        if self._active_index_cache:
            return self._active_index_cache

        is_alpha_active = await self._is_index_active(SEARCH_INDEX_NAME_ALPHA)
        if is_alpha_active:
            self._active_index_cache = SEARCH_INDEX_NAME_ALPHA
            return SEARCH_INDEX_NAME_ALPHA

        is_beta_active = await self._is_index_active(SEARCH_INDEX_NAME_BETA)
        if is_beta_active:
            self._active_index_cache = SEARCH_INDEX_NAME_BETA
            return SEARCH_INDEX_NAME_BETA

        # no active indices, but it's ok, return this one
        return SEARCH_INDEX_NAME_ALPHA

    async def _is_index_active(self, index_name: str) -> bool:
        return await self.elasticsearch_connection.indices.exists_alias(
            name=ACTIVE_SEARCH_INDEX_ALIAS, index=index_name
        )

    async def does_active_index_exist(self) -> bool:
        return any(
            await asyncio.gather(
                *[
                    self._is_index_active(SEARCH_INDEX_NAME_ALPHA),
                    self._is_index_active(SEARCH_INDEX_NAME_BETA),
                ]
            )
        )

    async def activate_index(self, index_name: str) -> None:
        this_index_active = await self.elasticsearch_connection.indices.exists_alias(
            name=ACTIVE_SEARCH_INDEX_ALIAS, index=index_name
        )
        if this_index_active:
            logger.info(
                f"index {index_name} already tied to alias {ACTIVE_SEARCH_INDEX_ALIAS}, do nothing"
            )
            return None

        some_index_active = await self.elasticsearch_connection.indices.exists_alias(
            name=ACTIVE_SEARCH_INDEX_ALIAS
        )
        if some_index_active:
            logger.warning(
                f"alias {ACTIVE_SEARCH_INDEX_ALIAS} tied to a different index, "
                f"human intervention required"
            )
            return None

        await self.elasticsearch_connection.indices.put_alias(
            index=index_name, name=ACTIVE_SEARCH_INDEX_ALIAS
        )

    async def get_inactive_write_index_name(self, check_exists: bool = False) -> str:
        if self._inactive_index_cache:
            return self._inactive_index_cache

        active_index_name = await self.get_active_write_index_name()
        if active_index_name == SEARCH_INDEX_NAME_ALPHA:
            self._inactive_index_cache = SEARCH_INDEX_NAME_BETA
        else:
            self._inactive_index_cache = SEARCH_INDEX_NAME_ALPHA

        if self._inactive_index_cache is None:
            raise AssertionError(
                "either SEARCH_INDEX_NAME_ALPHA or SEARCH_INDEX_NAME_BETA is not set"
            )

        if check_exists:
            if await self._is_existing_index(self._inactive_index_cache):
                # log that the invariant is broken, then proceed and hope for the best
                logger.error(f"{self._inactive_index_cache} already exists")

        return self._inactive_index_cache

    async def _is_existing_index(self, index: str) -> bool:
        return await self.elasticsearch_connection.indices.exists(index=index)

    async def switch_active_index(self) -> None:
        """Переключает активный индекс.

        Перед переключением делает насильный /refresh новому индексу,
        удостоверяясь таким образом, что документы в индексе доступны.

        Из-за /refresh может упасть по ConnectionTimeout, но это
        маловероятно из-за большого таймаута.
        """
        from_index = await self.get_active_write_index_name()
        to_index = await self.get_inactive_write_index_name()

        await self._refresh_index(to_index)

        await self._switch_active_index(from_index, to_index)
        self._reset_cache()
        formerly_active_index_name = from_index

        await self._delete_index(formerly_active_index_name)

    async def _switch_active_index(self, from_index: str, to_index: str) -> None:
        await self.elasticsearch_connection.indices.update_aliases(
            body={
                "actions": [
                    {
                        "remove": {
                            "index": from_index,
                            "alias": ACTIVE_SEARCH_INDEX_ALIAS,
                        }
                    },
                    {
                        "add": {
                            "index": to_index,
                            "alias": ACTIVE_SEARCH_INDEX_ALIAS,
                        }
                    },
                ]
            }
        )

    def _reset_cache(self) -> None:
        self._active_index_cache = None
        self._inactive_index_cache = None

    async def _refresh_index(self, index_name: str) -> None:
        """Заставляет индекс обнаружить свои документы как можно раньше."""
        await self.elasticsearch_connection.indices.refresh(
            index=index_name,
            request_timeout=60 * 10,  # это не быстрая операция
        )

    async def _delete_index(self, index: str) -> None:
        await self.elasticsearch_connection.indices.delete(index=index, ignore=[404])


@contextlib.asynccontextmanager
async def determine_writing_index_name(
    index_manager: IndexManager, is_mapping_changed: bool
) -> AsyncIterator[str]:
    try:
        if is_mapping_changed:
            index_name = await index_manager.get_inactive_write_index_name()
        else:
            index_name = await index_manager.get_active_write_index_name()
        yield index_name
    except Exception as ex:
        logger.exception(ex)
    else:
        if not await index_manager.does_active_index_exist():
            await index_manager.activate_index(index_name)
        elif is_mapping_changed:
            await index_manager.switch_active_index()
