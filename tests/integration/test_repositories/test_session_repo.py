from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.clock import Clock
from domain.models.session import Session
from infrastructure.db.models import SessionModel
from infrastructure.repositories.session import SQLiteSessionRepository


@pytest.mark.asyncio
async def test_get_active_session(sqlite_session: AsyncSession, mock_clock: Clock):
    repo = SQLiteSessionRepository(sqlite_session)

    now = mock_clock.now()

    sqlite_session.add(SessionModel(user_id=1, clock_in=now, clock_out=None))
    await sqlite_session.flush()

    result = await repo.get_active_by_user(1)

    assert result is not None
    assert result.is_active
    assert result.user_id == 1


@pytest.mark.asyncio
async def test_unique_open_session_per_user(
    sqlite_session: AsyncSession, mock_clock: Clock
):
    now = mock_clock.now()

    sqlite_session.add(SessionModel(user_id=1, clock_in=now, clock_out=None))
    sqlite_session.add(SessionModel(user_id=1, clock_in=now, clock_out=None))

    with pytest.raises(IntegrityError):
        await sqlite_session.flush()


@pytest.mark.asyncio
async def test_saves_new_session(sqlite_session: AsyncSession, mock_clock: Clock):
    repo = SQLiteSessionRepository(sqlite_session)
    now = mock_clock.now()

    await repo.save(Session.start(1, now))

    result = await sqlite_session.execute(select(SessionModel))
    result = result.scalars().all()

    assert len(result) == 1
    result = result[0]
    assert result.user_id == 1
    assert result.clock_in == now
    assert result.clock_out is None


@pytest.mark.asyncio
async def test_saves_existing_session(sqlite_session: AsyncSession, mock_clock: Clock):
    repo = SQLiteSessionRepository(sqlite_session)
    now = mock_clock.now()

    await repo.save(Session.start(1, now))
    await repo.save(Session.start(2, now))

    active = await repo.get_active_by_user(2)
    assert active is not None
    end = now + timedelta(hours=8)
    active.close(end)
    await repo.save(active)

    assert await repo.get_active_by_user(2) is None
    session = await sqlite_session.execute(
        select(SessionModel).where(SessionModel.user_id == 2)
    )
    session = session.scalars().one()
    assert session.user_id == 2
    assert session.clock_in == now
    assert session.clock_out == end


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sessions_data, start, end, expected_count",
    [
        # ✅ single session inside range
        (
            [datetime(2026, 3, 2, 7, tzinfo=UTC)],
            datetime(2026, 3, 2, 0, tzinfo=UTC),
            datetime(2026, 3, 3, 0, tzinfo=UTC),
            1,
        ),
        # ❌ session before range
        (
            [datetime(2026, 3, 1, 23, tzinfo=UTC)],
            datetime(2026, 3, 2, 0, tzinfo=UTC),
            datetime(2026, 3, 3, 0, tzinfo=UTC),
            0,
        ),
        # ❌ session exactly at end (excluded)
        (
            [datetime(2026, 3, 3, 0, tzinfo=UTC)],
            datetime(2026, 3, 2, 0, tzinfo=UTC),
            datetime(2026, 3, 3, 0, tzinfo=UTC),
            0,
        ),
        # ✅ multiple sessions, mixed
        (
            [
                datetime(2026, 3, 1, 23, tzinfo=UTC),  # out
                datetime(2026, 3, 2, 1, tzinfo=UTC),  # in
                datetime(2026, 3, 2, 5, tzinfo=UTC),  # in
                datetime(2026, 3, 3, 0, tzinfo=UTC),  # out
            ],
            datetime(2026, 3, 2, 0, tzinfo=UTC),
            datetime(2026, 3, 3, 0, tzinfo=UTC),
            2,
        ),
        # ✅ empty DB
        (
            [],
            datetime(2026, 3, 2, 0, tzinfo=UTC),
            datetime(2026, 3, 3, 0, tzinfo=UTC),
            0,
        ),
    ],
)
async def test_get_for_period_by_user(
    sqlite_session: AsyncSession,
    sessions_data: list[datetime],
    start: datetime,
    end: datetime,
    expected_count: int,
):
    user_id = 1
    repo = SQLiteSessionRepository(sqlite_session)

    # Arrange
    for i, clock_in in enumerate(sessions_data):
        sqlite_session.add(
            SessionModel(
                id=i + 1,
                user_id=user_id,
                clock_in=clock_in,
                clock_out=clock_in + timedelta(hours=8),
            )
        )
    await sqlite_session.flush()

    # Act
    result = await repo.get_for_period_by_user(user_id, start, end)

    # Assert
    assert len(result) == expected_count

    # extra safety: ensure all returned sessions are within range
    for session in result:
        assert start <= session.clock_in < end
