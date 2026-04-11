from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from infrastructure.db.config import DBConfig
from infrastructure.db.models import Base


def create_engine(config: DBConfig):
    return create_async_engine(
        config.url,
        echo=False,
        future=True,
    )


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
