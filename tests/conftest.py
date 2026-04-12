from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.clock import Clock
from domain.models.session import Session
from domain.models.user import User
from domain.repositories.session import SessionRepository
from domain.repositories.user import UserRepository
from infrastructure.db.config import DBConfig
from infrastructure.db.engine import create_engine, init_db
from infrastructure.db.session import create_session_maker, get_session


class MockUserRepository(UserRepository):
    """Has users [User("Adam", id=1), User("Eve", id=2)]"""

    def __init__(self) -> None:
        self._users: dict[int, User] = {1: User("Adam", id=1), 2: User("Eve", id=2)}

    async def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def add(self, user: User) -> bool:
        if user.id is None:
            raise ValueError("User's id can not be None")
        self._users[user.id] = user
        return True


@pytest.fixture
def mock_user_repo():
    return MockUserRepository()


class MockSessionRepository(SessionRepository):  # TODO: simplify this mock
    """Has sessions for two users (id: 1, 2) for 60 days 8 hours each day, since 01.01.0001 and one open after that."""

    count: int = 0

    def __init__(self) -> None:
        self._sessions: dict[int, list[Session]] = {}

        for user_id in range(1, 3):
            self._sessions[user_id] = []
            for day in range(60):
                start = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=day)
                session = Session.start(user_id, start)
                session.id = self.count
                self.count += 1
                session.close(start + timedelta(hours=8))
                self._sessions[user_id].append(session)
            open_session = Session.start(
                user_id, datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=60)
            )
            open_session.id = self.count
            self._sessions[user_id].append(open_session)

    async def get_active_by_user(self, user_id: int) -> Session | None:
        try:
            return next(s for s in self._sessions[user_id] if s.is_active)
        except StopIteration:
            return None

    async def get_for_period_by_user(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Session]:
        return [
            s
            for s in self._sessions[user_id]
            if s.clock_in >= start and s.clock_in < end
        ]

    async def save(self, session: Session) -> Session:
        if session.user_id not in self._sessions:
            raise ValueError("Can not create or update session, user does not exist")
        for i, sess in enumerate(self._sessions[session.user_id]):
            if sess.id == session.id:
                self._sessions[session.user_id][i] = session
                return session

        self._sessions[session.user_id].append(session)
        return session


@pytest.fixture
def mock_session_repo():
    return MockSessionRepository()


class MockClock(Clock):
    """now is 2026-03-02 08:00:00+00:00"""

    def now(self) -> datetime:
        return datetime(2026, 3, 2, 8, tzinfo=UTC)


@pytest.fixture
def mock_clock():
    return MockClock()


@pytest_asyncio.fixture(scope="session")
async def sqlite_engine() -> AsyncEngine:
    config = DBConfig(url="sqlite+aiosqlite:///:memory:")
    engine = create_engine(config)
    await init_db(engine)
    return engine


@pytest.fixture(scope="session")
def sqlite_sesionmaker(sqlite_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    sessionmaker = create_session_maker(sqlite_engine)
    return sessionmaker


@pytest_asyncio.fixture
async def sqlite_session(sqlite_sesionmaker: async_sessionmaker[AsyncSession]):
    async with get_session(sqlite_sesionmaker) as session:
        yield session
        await session.rollback()
