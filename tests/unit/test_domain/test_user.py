import pytest

from domain.models.user import User


def test_user_requires_id():
    with pytest.raises(ValueError, match="User must be initialized with id"):
        User("test user")


def test_user_initializes():
    user = User("test", id=12345)
    assert user.name == "test"
    assert user.id == 12345
