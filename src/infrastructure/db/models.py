from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy_utc import UtcDateTime

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


class SessionModel(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True
    )
    clock_in: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
    clock_out: Mapped[datetime | None] = mapped_column(UtcDateTime, nullable=True)
    __table_args__ = (
        sa.Index("ix_sessions_user_id_clock_in", "user_id", "clock_in"),
        sa.Index(
            "uq_active_session_per_user",
            "user_id",
            unique=True,
            sqlite_where=sa.text("clock_out IS NULL"),
        ),
    )
