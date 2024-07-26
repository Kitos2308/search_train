import asyncio
from app.core.indexing.index_repository import IndexingRepository
from app.infrastracture.database import Database
from app.core.searching.repository import SearchingRepository
from app.settings import settings
from elasticsearch import AsyncElasticsearch
from app.core.indexing.index_service import IndexingService
from app.core.indexing.index_manager import IndexManager, determine_writing_index_name
from app.core.indexing.index_mapper import IndexDocument

_search_connection = AsyncElasticsearch(
    hosts=['http://localhost:9200'],
    connections_per_node=10,
    retry_on_timeout=True,
)




async def _is_index_active(index_name: str) -> bool:
    return await _search_connection.indices.exists_alias(
        name=settings.ACTIVE_SEARCH_INDEX_ALIAS, index=index_name
    )


async def get_active_write_index_name() -> str:
    is_alpha_active = await _is_index_active(settings.SEARCH_INDEX_NAME_ALPHA)
    if is_alpha_active:
        _active_index_cache = settings.SEARCH_INDEX_NAME_ALPHA
        return settings.SEARCH_INDEX_NAME_ALPHA


async def elastic_indexing():
    index_manager = IndexManager(elasticsearch_connection=_search_connection)
    async with determine_writing_index_name(
            index_manager, is_mapping_changed=False
    ) as write_index:
        index_service = IndexingService(repository=IndexingRepository(using=_search_connection))
        await IndexDocument.initialize(
            target_index=write_index, using=_search_connection
        )
        await index_service.chunked_add_documents(write_index)
        # await _search_connection.indices.refresh(index=SEARCH_INDEX_NAME_ALPHA)


async def elastic_searching(query:str):
    searching_repository = SearchingRepository(using=_search_connection)
    s = await searching_repository.search(query)
    print(s)


if __name__ == '__main__':
    Database.create_engine(settings)

    loop = asyncio.get_event_loop()



    loop.run_until_complete(elastic_indexing())

    # loop.run_until_complete(elastic_searching('Скоро откроется дачный сезон'))