from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def create_session_maker(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session(sessionmaker: async_sessionmaker[AsyncSession]):
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
