from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from starlette.requests import Request

from app.core.searching.service import SearchingService
from app.core.searching.repository import SearchingRepository


def get_search_connection(request: Request) -> AsyncElasticsearch:
    return request.app.state.search_connection


def get_searching_repository(
    search_connection: AsyncElasticsearch = Depends(
        get_search_connection, use_cache=True
    )
) -> SearchingRepository:
    return SearchingRepository(using=search_connection)


def get_searching_service(
    repository: SearchingRepository = Depends(get_searching_repository, use_cache=True),
) -> SearchingService:
    return SearchingService(repository=repository)
