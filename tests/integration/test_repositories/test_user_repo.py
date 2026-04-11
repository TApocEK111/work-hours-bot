import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.user import User
from infrastructure.db.models import UserModel
from infrastructure.repositories.user import SQLiteUserRepository


@pytest.mark.asyncio
async def test_adds_user(sqlite_session: AsyncSession):
    repo = SQLiteUserRepository(sqlite_session)

    await repo.add(User("Test User", id=1234))

    new_user = await sqlite_session.execute(select(UserModel))
    new_user = new_user.scalars().all()

    assert len(new_user) == 1
    new_user = new_user[0]
    assert new_user.id == 1234
    assert new_user.name == "Test User"


@pytest.mark.asyncio
async def test_user_unique_constraint(sqlite_session: AsyncSession):
    repo = SQLiteUserRepository(sqlite_session)
    first = await repo.add(User("Test User", id=1234))
    second = await repo.add(User("Test", id=1234))

    assert first
    assert not second


@pytest.mark.asyncio
async def test_gets_user_by_id(sqlite_session: AsyncSession):
    repo = SQLiteUserRepository(sqlite_session)
    sqlite_session.add_all(
        [UserModel(name="Test User", id=123), UserModel(name="Test", id=1234)]
    )
    await sqlite_session.flush()

    user1 = await repo.get_by_id(123)
    user2 = await repo.get_by_id(1234)

    assert user1 is not None
    assert user1.id == 123
    assert user1.name == "Test User"
    assert user2 is not None
    assert user2.id == 1234
    assert user2.name == "Test"
