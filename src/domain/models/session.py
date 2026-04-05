from dataclasses import dataclass
from datetime import datetime, timedelta

from domain.models.entity import Entity


@dataclass
class Session(Entity):
    user_id: int
    clock_in: datetime
    clock_out: datetime | None = None

    def __post_init__(self):
        self._ensure_aware(self.clock_in, "clock_in")
        self._ensure_tz_consistency()

    @classmethod
    def start(cls, user_id: int, when: datetime) -> "Session":
        if when.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        return cls(user_id=user_id, clock_in=when)

    @staticmethod
    def _ensure_aware(dt: datetime, field: str):
        if dt.tzinfo is None:
            raise ValueError(f"{field} must be timezone-aware")

    def _ensure_after_clock_in(self, dt: datetime, field: str):
        if dt < self.clock_in:
            raise ValueError(f"{field} cannot be before clock_in")

    def _ensure_tz_consistency(self):
        if self.clock_out and self.clock_out.tzinfo != self.clock_in.tzinfo:
            raise ValueError("clock_out must use same timezone as clock_in")

    @property
    def is_active(self) -> bool:
        return self.clock_out is None

    def duration(self, now: datetime) -> timedelta:
        self._ensure_aware(now, "now")
        self._ensure_after_clock_in(now, "now")
        end = self.clock_out or now
        return end - self.clock_in

    def close(self, when: datetime) -> None:
        self._ensure_aware(when, "when")
        self._ensure_after_clock_in(when, "when")
        if not self.is_active:
            raise ValueError("Session already closed")
        self.clock_out = when
        self._ensure_tz_consistency()
