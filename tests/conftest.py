import asyncio
from typing import AsyncIterator, Iterator

import pytest
from elasticsearch import Elasticsearch

from app.infrastructure.database import Database
from app.settings import settings


@pytest.fixture(scope="session")
def search_connection() -> Iterator[Elasticsearch]:
    connection = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST], maxsize=1)
    yield connection
    connection.close()


@pytest.fixture(autouse=True)
def cleanup(search_connection: Elasticsearch) -> Iterator[None]:
    yield
    search_connection.indices.delete(index=settings.SEARCH_INDEX_NAME_ALPHA, ignore=[404])
    search_connection.indices.delete(index=settings.SEARCH_INDEX_NAME_BETA, ignore=[404])


@pytest.fixture(scope="session")
def event_loop(request):  # type: ignore
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_connection() -> AsyncIterator[Database]:
    Database.create_engine(settings)
    return
