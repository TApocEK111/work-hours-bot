from datetime import datetime, timedelta

from application.clock import Clock
from application.exceptions import AlreadyClockedInError, NoActiveSessionError
from domain.models.session import Session
from domain.repositories.session import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository, clock: Clock) -> None:
        self._repo = repository
        self._clock = clock
        now = self._clock.now()
        if now.tzinfo is None:
            raise RuntimeError("Clock must return timezone-aware datetime")

    @staticmethod
    def _start_of_day(dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)

    @staticmethod
    def _start_of_week(dt: datetime) -> datetime:
        monday = dt - timedelta(days=dt.weekday())
        return datetime(monday.year, monday.month, monday.day, tzinfo=dt.tzinfo)

    @staticmethod
    def _start_of_month(dt: datetime) -> datetime:
        return datetime(dt.year, dt.month, 1, tzinfo=dt.tzinfo)

    async def clock_in_user(self, user_id: int) -> Session:
        if await self._repo.get_active_by_user(user_id):
            raise AlreadyClockedInError(f"User {user_id} already has active session")
        new_session = Session.start(user_id, self._clock.now())
        return await self._repo.save(new_session)

    async def clock_out_user(self, user_id: int) -> Session:
        current_session = await self._repo.get_active_by_user(user_id)
        if not current_session:
            raise NoActiveSessionError(f"No active session for user {user_id}")
        current_session.close(self._clock.now())
        return await self._repo.save(current_session)

    async def get_today_sessions_by_user(self, user_id: int) -> list[Session]:
        now = self._clock.now()
        start = self._start_of_day(now)
        return await self._repo.get_for_period_by_user(user_id, start, now)

    async def get_this_week_sessions_by_user(self, user_id: int) -> list[Session]:
        now = self._clock.now()
        start = self._start_of_week(now)
        return await self._repo.get_for_period_by_user(user_id, start, now)

    async def get_this_month_sessions_by_user(self, user_id: int) -> list[Session]:
        now = self._clock.now()
        start = self._start_of_month(now)
        return await self._repo.get_for_period_by_user(user_id, start, now)

    def sum_duration(self, sessions: list[Session]) -> timedelta:
        total = timedelta()
        for session in sessions:
            total += session.duration(self._clock.now())
        return total
