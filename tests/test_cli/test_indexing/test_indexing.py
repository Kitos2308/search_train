import datetime

import pytest
from elasticsearch import Elasticsearch
from sqlalchemy.ext.asyncio import AsyncSession
from typer import Typer
from typer.testing import CliRunner

from app.settings import settings
from tests.test_cli.test_indexing.conftest import CursorMock

runner = CliRunner()


@pytest.fixture()
def article_text_mock() -> CursorMock:
    return CursorMock(
        [
            {
                "meta_id": "100_article",
                "type": "article",
                "text": "Что такое премия «Оскар»? ",
                "img": "/home/news/20160226/oscar.jpg",
                "entity_date": datetime.datetime(2016, 2, 27, 12, 15, tzinfo=datetime.timezone.utc),
            },
            {
                "meta_id": "101_article",
                "type": "article",
                "text": "Что такое телевидение",
                "img": "/home/news/20160226/oscar.jpg",
                "entity_date": datetime.datetime(2016, 2, 27, 12, 15, tzinfo=datetime.timezone.utc),
            },
        ],
    )


@pytest.mark.parametrize(
    "expected_received_documents",
    [
        {"Что такое премия «Оскар»? ", "Что такое телевидение"},
    ],
)
def test_full_reindex(
    mocker,
    cli_app: Typer,
    article_text_mock: CursorMock,
    search_connection: Elasticsearch,
    expected_received_documents,
) -> None:
    mocker.patch.object(
        AsyncSession,
        "execute",
        side_effect=[
            article_text_mock,
        ],
    )
    cli_result = runner.invoke(
        cli_app,
        [
            "indexing",
            "start-full-reindex",
        ],
    )

    search_connection.indices.refresh(index=settings.ACTIVE_SEARCH_INDEX_ALIAS)
    search_result = search_connection.search(body={"query": {"match_all": {}}}, index=settings.ACTIVE_SEARCH_INDEX_ALIAS)
    received_documents = {hit["_source"]["primary_field"] for hit in search_result["hits"]["hits"]}
    assert cli_result.exit_code == 0, cli_result.stdout
    assert received_documents == expected_received_documents
