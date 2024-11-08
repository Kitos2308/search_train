import logging

from fastapi import APIRouter, Depends, Form, Request
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.core.searching.service import SearchingService
from .deps import get_searching_service

router = APIRouter()

templates = Jinja2Templates(directory="utils/templates", auto_reload=True)

logger = logging.getLogger("api application")


@router.get("", tags=["Test Stand"])
async def search_index(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("searching.html", {"request": request, "articles": []})


@router.post("")
async def search_query(
    request: Request,
    searching_service: SearchingService = Depends(get_searching_service),
    value: str = Form(),
):
    logger.info(f"start query with value = {value}")
    result = await searching_service.get_most_relevant_result(value)
    return templates.TemplateResponse("searching.html", {"request": request, "articles": result.hits})
