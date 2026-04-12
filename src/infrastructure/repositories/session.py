from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError

from application.exceptions import NoUserError
from domain.models.session import Session
from domain.repositories.session import SessionRepository
from infrastructure.db.models import SessionModel
from infrastructure.repositories.async_base import BaseAsyncAlchemyRepository


class SQLiteSessionRepository(SessionRepository, BaseAsyncAlchemyRepository):
    """Async SQLAlchemy SQLite3 Session repository"""

    @staticmethod
    def _to_domain(model: SessionModel) -> Session:
        return Session(model.user_id, model.clock_in, model.clock_out, id=model.id)

    @staticmethod
    def _to_model(session: Session) -> SessionModel:
        return SessionModel(
            user_id=session.user_id,
            clock_in=session.clock_in,
            clock_out=session.clock_out,
            id=session.id,
        )

    async def get_active_by_user(self, user_id: int) -> Session | None:
        query = select(SessionModel).where(
            and_(SessionModel.user_id == user_id, SessionModel.clock_out.is_(None))
        )
        result = await self._db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return self._to_domain(user)

    async def get_for_period_by_user(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Session]:
        """End is excluded."""
        query = select(SessionModel).where(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.clock_in >= start,
                SessionModel.clock_in < end,
            )
        )
        result = await self._db.execute(query)
        session_rows = result.scalars().all()
        return [self._to_domain(row) for row in session_rows]

    async def save(self, session: Session) -> Session:
        if session.id:
            session_model = await self._db.get(SessionModel, session.id)
            if session_model:
                session_model.clock_in = session.clock_in
                session_model.clock_out = session.clock_out
                session_model.user_id = session.user_id
            else:
                session_model = self._to_model(session)
                self._db.add(session_model)
        else:
            session_model = self._to_model(session)
            self._db.add(session_model)

        try:
            await self._db.flush()
        except IntegrityError:
            raise NoUserError
        await self._db.refresh(session_model)

        return self._to_domain(session_model)
