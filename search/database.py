from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .settings import Settings


class Database:
    engine: AsyncEngine | None = None
    session_maker: async_sessionmaker | None = None

    @classmethod
    def create_engine(cls,
                      settings: Settings,
                      dsn: str | None = None,
                      application_name: str = ''):
        if dsn is None:
            dsn = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

        cls.engine = create_async_engine(
            dsn,
            echo=settings.DB_ECHO_QUERIES,
            connect_args={"timeout": settings.DB_TIMEOUT, "server_settings": {
                "application_name": f"{settings.ENVIRONMENT}/{settings.SERVICE_NAME}/{application_name}"}},
            pool_size=settings.DB_POOL_SIZE
        )

        cls.session_maker = async_sessionmaker(
            cls.engine.execution_options(schema_translate_map={None: settings.DB_SCHEMA}),
            expire_on_commit=settings.DB_SESSION_EXPIRE_ON_COMMIT,
            autocommit=settings.DB_SESSION_AUTOCOMMIT,
            autoflush=settings.DB_SESSION_AUTOFLUSH
        )

    @classmethod
    async def stop(cls):
        if cls.engine:
            await cls.engine.dispose()
        else:
            logging.warning('No engine to dispose')

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        if cls.engine is None or cls.session_maker is None:
            raise Exception('No engine or session_maker')

        session: AsyncSession = cls.session_maker()
        try:
            yield session
        except Exception as e:
            logging.error(e)
            await session.rollback()
            raise
        finally:
            await session.close()
