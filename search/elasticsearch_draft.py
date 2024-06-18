import asyncio
import logging

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncDocument

from search.index_manager import IndexManager, determine_writing_index_name

_search_connection = AsyncElasticsearch(
            hosts=['http://localhost:9200'],
            connections_per_node=10,
            retry_on_timeout=True,
        )

SEARCH_INDEX_NAME_ALPHA = "searchable-document-index-alpha"
SEARCH_INDEX_NAME_BETA = "searchable-document-index-beta"
ACTIVE_SEARCH_INDEX_ALIAS = "searchable-document-index-alias"


async def _is_index_active(index_name: str) -> bool:
    return await _search_connection.indices.exists_alias(
        name=ACTIVE_SEARCH_INDEX_ALIAS, index=index_name
    )

async def get_active_write_index_name() -> str:

    is_alpha_active = await _is_index_active(SEARCH_INDEX_NAME_ALPHA)
    if is_alpha_active:
        _active_index_cache = SEARCH_INDEX_NAME_ALPHA
        return SEARCH_INDEX_NAME_ALPHA




class IndexDocument(AsyncDocument):

    @classmethod
    async def initialize(
        cls, target_index: str, using: AsyncElasticsearch = None
    ) -> None:
        """
        Create the index and populate the mappings if the index does not exist.

        Same as Document.init, but if the index already exists, the method skips the mapping update
        """
        new_index = cls._index.clone(name=target_index)
        if not await new_index.exists(using=using):
            logging.info("index doesn't exist, create it")
            await new_index.create(using=using)
            cls._index = new_index
        else:
            logging.info("index already exists, skip the creation")



async def elastic():
    index_manager = IndexManager(elasticsearch_connection=_search_connection)
    async with determine_writing_index_name(
        index_manager, is_mapping_changed=False
    ) as write_index:
        await IndexDocument.initialize(
            target_index=write_index, using=_search_connection
        )


if __name__=='__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(get_active_write_index_name())

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(IndexDocument.initialize('second', using=_search_connection))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(elastic())



