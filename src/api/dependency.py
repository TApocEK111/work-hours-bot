from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.clock import Clock
from application.services.session import SessionService
from application.services.user import UserService
from infrastructure.repositories.session import SQLiteSessionRepository
from infrastructure.repositories.user import SQLiteUserRepository


class Container:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession], clock: Clock):
        self.session_maker = session_maker
        self.clock = clock

    def get_session_service(self, session: AsyncSession) -> SessionService:
        repo = SQLiteSessionRepository(session)
        return SessionService(repo, self.clock)

    def get_user_service(self, session: AsyncSession) -> UserService:
        repo = SQLiteUserRepository(session)
        return UserService(repo)
