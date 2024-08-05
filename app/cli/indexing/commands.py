import asyncio
import logging

from typer import Typer
from app.core.indexing.index_repository import IndexingRepository
from app.infrastructure.database import Database
from app.settings import settings
from elasticsearch import AsyncElasticsearch
from app.core.indexing.index_service import IndexingService
from app.core.indexing.index_manager import IndexManager, determine_writing_index_name
from app.core.indexing.index_mapper import IndexDocument
from app.infrastructure.fill_source_data import mapper_data, bulk_insert_data

_search_connection = AsyncElasticsearch(
    hosts=['http://localhost:9200'],
    connections_per_node=10,
    retry_on_timeout=True,
)

app = Typer(name="indexing")


logger = logging.getLogger("cli app")


async def _is_index_active(index_name: str) -> bool:
    return await _search_connection.indices.exists_alias(
        name=settings.ACTIVE_SEARCH_INDEX_ALIAS, index=index_name
    )


async def get_active_write_index_name() -> str:
    is_alpha_active = await _is_index_active(settings.SEARCH_INDEX_NAME_ALPHA)
    if is_alpha_active:
        _active_index_cache = settings.SEARCH_INDEX_NAME_ALPHA
        return settings.SEARCH_INDEX_NAME_ALPHA


async def _start_full_reindex():
    logger.info('start reindex')
    index_manager = IndexManager(elasticsearch_connection=_search_connection)
    async with determine_writing_index_name(
            index_manager, is_mapping_changed=False
    ) as write_index:
        index_service = IndexingService(repository=IndexingRepository(using=_search_connection))
        await IndexDocument.initialize(
            target_index=write_index, using=_search_connection
        )
        await index_service.chunked_add_documents(write_index)
        # await _search_connection.indices.refresh(index=SEARCH_INDEX_NAME_ALPHA) #todo сделать рефреш чтобы убедиться что индекс обновился?


@app.command()
def start_full_reindex():
    asyncio.run(_start_full_reindex())


@app.command()
def fill_data_postgres():
    Database.create_engine(settings)
    data = mapper_data()
    asyncio.run(bulk_insert_data(data))