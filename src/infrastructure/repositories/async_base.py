from sqlalchemy.ext.asyncio import AsyncSession


class BaseAsyncAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._db = session
