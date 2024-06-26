from fastapi import APIRouter, Depends, Query, Request

from app.api.searching.service import SearchingService
from .deps import get_searching_service

router = APIRouter()


@router.get('/search')
async def authorize_with_yandex_redirect(
        request: Request,
        query: str,
        searching_service: SearchingService = Depends(get_searching_service),
):
    result = await searching_service.get_most_relevant_result(query)
    return result
