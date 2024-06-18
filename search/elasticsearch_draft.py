import asyncio
import logging

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncDocument

from search.index_manager import IndexManager, determine_writing_index_name
from search.index_mapper import IndexDocument

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



