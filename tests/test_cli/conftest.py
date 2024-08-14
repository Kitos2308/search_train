from typing import Iterator

import pytest
from elasticsearch import Elasticsearch
from typer import Typer

from app.cli.typer_app import get_app
from app.infrastructure.database import Database


@pytest.fixture()
def cli_app(search_connection: Elasticsearch, db_connection: Database) -> Iterator[Typer]:
    return get_app()
