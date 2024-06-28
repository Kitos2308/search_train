import os
import sys

from fastapi import APIRouter, Depends, Query, Request, Form
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.api.searching.service import SearchingService
from .deps import get_searching_service

router = APIRouter()

templates = Jinja2Templates(directory='utils/templates', auto_reload=True)


@router.get("", tags=["Test Stand"])
async def search_index(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("searching.html", {"request": request})


@router.post('')
async def authorize_with_yandex_redirect(
        request: Request,
        searching_service: SearchingService = Depends(get_searching_service),
        value: str = Form()):

    print(value)
    result = await searching_service.get_most_relevant_result('query')
    return result
