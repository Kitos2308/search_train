import asyncio
import logging
from typing import Any

import sentry_sdk
from typer import Context, Typer

from app.cli.indexing.commands import app as cli_app
from app.infrastructure.cutom_logging import CustomFormatter
from app.infrastructure.database import Database
from app.main_app import Application
from app.settings import settings


class CLIApplication:
    def __init__(self) -> None:
        self._db_connection = Database.create_engine(settings)

    def setup(self) -> Typer:
        self.main_app = Application()

        self.app = Typer(
            name="Elastic Python Search CLI",
            callback=self.startup,
            result_callback=self.shutdown,
        )
        self.app.add_typer(cli_app)

        self.add_sentry()

        self.setup_logging()

        return self.app

    def startup(self, ctx: Context) -> None:
        asyncio.run(self.main_app.startup())
        ctx.obj = {
            "search_connection": self.main_app.search_connection,
            "db_connection": self._db_connection,
            "current_index_name": settings.SEARCH_INDEX_NAME_ALPHA,
        }

    def shutdown(self, *args: Any, **kwargs: Any) -> None:
        asyncio.run(self.main_app.shutdown())

    @staticmethod
    def add_sentry() -> None:
        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                debug=settings.DEBUG,
                default_integrations=True,
            )

    @staticmethod
    def setup_logging() -> None:
        level_logging = logging.DEBUG if settings.ENVIRONMENT in ["local", "test"] else logging.WARNING

        logger = logging.getLogger("cli app")
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(level_logging)

        ch.setFormatter(CustomFormatter())

        logger.addHandler(ch)


def get_app() -> Typer:
    return CLIApplication().setup()


if __name__ == "__main__":
    app = get_app()
    app()
