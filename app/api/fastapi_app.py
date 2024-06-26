import asyncio

import sentry_sdk
import uvicorn
import uvloop
from app.settings import settings
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette_prometheus import PrometheusMiddleware, metrics
from .searching.views import router as searching_router
from app.main_app import Application

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class FastAPIApplication:
    def setup(self) -> FastAPI:
        main_app = Application()

        self.app = FastAPI(title="Elastic Python Search", debug=settings.DEBUG)
        self.app.state.search_connection = main_app.search_connection

        self.app.add_event_handler("shutdown", main_app.shutdown)

        self.app.add_route("/metrics", metrics)
        self.app.include_router(searching_router, prefix="/api/search", tags=["search"])

        self.add_middlewares()

        return self.app

    def add_middlewares(self) -> None:
        # self.app.add_middleware(PrometheusMiddleware)
        # self.app.add_middleware(ProfilingMiddleware)
        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                debug=settings.DEBUG,
                default_integrations=True,
            )
            # self.app.add_middleware(SentryAsgiMiddleware)


def get_app() -> FastAPI:
    return FastAPIApplication().setup()


app = get_app()


