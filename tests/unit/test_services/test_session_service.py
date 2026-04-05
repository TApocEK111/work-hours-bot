from datetime import timedelta

import pytest

from application.clock import Clock
from application.exceptions import AlreadyClockedInError, NoActiveSessionError
from application.services.session import SessionService
from domain.models.session import Session
from domain.repositories.session import SessionRepository


@pytest.fixture
def service(mock_session_repo: SessionRepository, mock_clock: Clock):
    return SessionService(mock_session_repo, mock_clock)


@pytest.mark.asyncio
async def test_clocks_out(service: SessionService, mock_clock: Clock):
    session = await service.clock_out_user(1)
    assert not session.is_active
    assert session.clock_out == mock_clock.now()


@pytest.mark.asyncio
async def test_clocks_in(service: SessionService, mock_clock: Clock):
    await service.clock_out_user(1)
    session = await service.clock_in_user(1)
    assert session.is_active
    assert session.clock_in == mock_clock.now()


@pytest.mark.asyncio
async def test_fails_second_clock_in(service: SessionService):
    with pytest.raises(AlreadyClockedInError):
        await service.clock_in_user(1)


@pytest.mark.asyncio
async def test_fails_second_clock_out(service: SessionService):
    await service.clock_out_user(1)
    with pytest.raises(NoActiveSessionError):
        await service.clock_out_user(1)


def check_session_range(
    sessions: list[Session],
    expected_length: int,
    service: SessionService,
):
    assert len(sessions) == expected_length

    assert service.sum_duration(sessions) == expected_length * timedelta(hours=8)


@pytest.mark.asyncio
async def test_gets_today_sessions(service: SessionService):
    check_session_range(await service.get_today_sessions_by_user(1), 1, service)


@pytest.mark.asyncio
async def test_gets_this_week_sessions(service: SessionService):
    check_session_range(await service.get_this_week_sessions_by_user(1), 1, service)


@pytest.mark.asyncio
async def test_gets_this_month_sessions(service: SessionService):
    check_session_range(await service.get_this_month_sessions_by_user(1), 2, service)
