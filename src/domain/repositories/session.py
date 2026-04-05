from abc import ABC, abstractmethod
from datetime import datetime

from domain.models.session import Session


class SessionRepository(ABC):
    @abstractmethod
    async def get_active_by_user(self, user_id: int) -> Session | None: ...

    @abstractmethod
    async def get_for_period_by_user(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[Session]:
        """End is excluded."""
        ...

    @abstractmethod
    async def save(self, session: Session) -> Session: ...
