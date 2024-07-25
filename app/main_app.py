from dynaconf import settings
from elasticsearch import AsyncElasticsearch

from app.core.indexing.index_manager import (
    IndexManager,
    determine_writing_index_name,
)
from app.core.indexing.index_mapper import IndexDocument


class Application:
    def __init__(self) -> None:
        self._search_connection = AsyncElasticsearch(
            hosts=['http://localhost:9200'],
            maxsize=10,
            retry_on_timeout=True,
        )

    async def shutdown(self) -> None:
        await self._close_current_search_connection_pool()

    async def startup(self) -> None:
        connection = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_HOST], maxsize=1)
        index_manager = IndexManager(connection)

        async with determine_writing_index_name(
            index_manager, is_mapping_changed=False
        ) as writing_index:
            await IndexDocument.initialize(target_index=writing_index, using=connection)

        await connection.close()

    @property
    def search_connection(self) -> AsyncElasticsearch:
        return self._search_connection

    async def _close_current_search_connection_pool(self) -> None:
        await self._search_connection.close()
