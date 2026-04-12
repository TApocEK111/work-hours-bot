import pytest

from application.exceptions import InvalidUserNameError, UserAlreadyExistsError
from application.services.user import UserService
from domain.repositories.user import UserRepository


@pytest.fixture
def service(mock_user_repo: UserRepository):
    return UserService(mock_user_repo)


@pytest.mark.asyncio
async def test_gets_user(service: UserService):
    user = await service.get_by_id(1)
    assert user is not None
    assert user.id == 1
    assert user.name == "Adam"


@pytest.mark.asyncio
async def test_gets_none(service: UserService):
    user = await service.get_by_id(3)
    assert user is None


@pytest.mark.asyncio
async def test_adds_user(service: UserService):
    assert await service.create(3, "Kain")


@pytest.mark.asyncio
async def test_fails_create_existing(service: UserService):
    with pytest.raises(UserAlreadyExistsError):
        await service.create(1, "Abraham")


@pytest.mark.asyncio
async def test_fails_create_empty_name(service: UserService):
    with pytest.raises(InvalidUserNameError):
        await service.create(3, "")
