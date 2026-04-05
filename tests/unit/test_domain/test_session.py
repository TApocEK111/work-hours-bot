from datetime import UTC, datetime, timedelta, timezone

import pytest

from domain.models.session import Session


@pytest.fixture
def started_session() -> tuple[Session, datetime]:
    start_time = datetime(2, 2, 2, tzinfo=UTC)
    return Session.start(1, start_time), start_time


@pytest.mark.parametrize(
    "user_id, start, end",
    [
        (1, datetime(1, 1, 1), None),
        (1, datetime(1, 1, 1, tzinfo=UTC), datetime(1, 1, 1)),
        (
            1,
            datetime(1, 1, 1, tzinfo=timezone(timedelta(hours=3))),
            datetime(1, 1, 1, tzinfo=UTC),
        ),
    ],
)
def test_requires_consistent_timezone(user_id: int, start: datetime, end: datetime):
    with pytest.raises(ValueError, match=r".*timezone.*"):
        if not end:
            Session(user_id, start)
        else:
            Session(user_id, start, end)


def test_requires_timezone_on_start():
    with pytest.raises(ValueError, match=r".*timezone.*"):
        Session.start(1, datetime(1, 1, 1))


def test_session_starts():
    start_time = datetime(1, 1, 1, tzinfo=UTC)
    session = Session.start(1, start_time)
    assert session.id is None
    assert session.user_id == 1
    assert session.clock_in == start_time
    assert session.clock_out is None
    assert session.is_active


@pytest.mark.parametrize(
    "end",
    [
        datetime(2, 2, 3),
        datetime(2, 2, 3, tzinfo=timezone(timedelta(hours=3))),
    ],
)
def test_close_requires_consistent_tz(
    end: datetime, started_session: tuple[Session, datetime]
):
    session, _ = started_session
    with pytest.raises(ValueError, match=r".*timezone.*"):
        session.close(end)


def test_start_close_flow(started_session: tuple[Session, datetime]):
    session, start_time = started_session
    assert session.is_active
    session.close(start_time + timedelta(hours=8))
    assert not session.is_active


def test_close_must_be_after(started_session: tuple[Session, datetime]):
    session, _ = started_session
    with pytest.raises(ValueError, match=r".*cannot be before.*"):
        session.close(datetime(2, 2, 1, tzinfo=UTC))


def test_close_session_must_be_open(started_session: tuple[Session, datetime]):
    session, start_time = started_session
    session.close(start_time + timedelta(hours=8))
    with pytest.raises(ValueError, match="Session already closed"):
        session.close(start_time + timedelta(hours=9))


def test_duration_requires_tz(started_session: tuple[Session, datetime]):
    session, _ = started_session
    with pytest.raises(ValueError, match=r".*timezone.*"):
        session.duration(datetime(2, 2, 3))


def test_negative_duration_fails(started_session: tuple[Session, datetime]):
    session, start_time = started_session
    with pytest.raises(ValueError, match=r"cannot be before clock_in"):
        session.duration(start_time - timedelta(hours=3))


@pytest.mark.parametrize(
    "delta",
    [
        timedelta(days=1),
        timedelta(hours=8),
        timedelta(hours=8, minutes=30),
    ],
)
def test_duration_correct(started_session: tuple[Session, datetime], delta: timedelta):
    session, start_time = started_session
    assert session.duration(start_time + delta) == delta


def test_duration_after_close(started_session: tuple[Session, datetime]):
    session, start = started_session
    end = start + timedelta(hours=5)
    session.close(end)

    assert session.duration(start + timedelta(days=1)) == timedelta(hours=5)
