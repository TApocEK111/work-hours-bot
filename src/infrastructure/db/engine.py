from typing import Any

from aiosqlite import Connection
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from infrastructure.db.config import DBConfig
from infrastructure.db.models import Base


def create_engine(config: DBConfig):
    engine = create_async_engine(
        config.url,
        echo=False,
        future=True,
    )

    if "sqlite" in config.url.lower():

        @event.listens_for(engine.sync_engine, "connect")
        def enable_sqlite_fk(dbapi_connection: Connection, connection_record: Any):  # pyright: ignore[reportUnusedFunction]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")  # type: ignore
            cursor.close()

    return engine


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
