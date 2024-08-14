import asyncio
import logging

from elasticsearch import AsyncElasticsearch
from typer import Typer

from app.core.indexing.index_manager import IndexManager, determine_writing_index_name
from app.core.indexing.index_mapper import IndexDocument
from app.core.indexing.index_repository import IndexingRepository
from app.core.indexing.index_service import IndexingService
from app.infrastructure.database import Database
from app.infrastructure.fill_source_data import bulk_insert_data, mapper_data
from app.settings import settings

_search_connection = AsyncElasticsearch(
    hosts=["http://localhost:9200"],
    connections_per_node=10,
    retry_on_timeout=True,
)

app = Typer(name="indexing")


logger = logging.getLogger("cli app")


async def _start_full_reindex() -> None:
    logger.info("start reindex")
    index_manager = IndexManager(elasticsearch_connection=_search_connection)
    async with determine_writing_index_name(index_manager, is_mapping_changed=False) as write_index:
        index_service = IndexingService(repository=IndexingRepository(using=_search_connection))
        await IndexDocument.initialize(target_index=write_index, using=_search_connection)
        await index_service.chunked_add_documents(write_index)
        # await _search_connection.indices.refresh(index=SEARCH_INDEX_NAME_ALPHA) #TODO сделать рефреш чтобы убедиться что индекс обновился?


@app.command()
def start_full_reindex() -> None:
    asyncio.run(_start_full_reindex())


@app.command()
def fill_data_postgres() -> None:
    Database.create_engine(settings)
    data = mapper_data()
    asyncio.run(bulk_insert_data(data))
