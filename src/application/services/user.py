from application.exceptions import InvalidUserNameError, UserAlreadyExistsError
from domain.models.user import User
from domain.repositories.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def get_by_id(self, id: int) -> User | None:
        return await self._repo.get_by_id(id)

    async def create(self, user_id: int, name: str) -> bool:
        if await self._repo.get_by_id(user_id):
            raise UserAlreadyExistsError(f"User {user_id} already exists")
        name = name.strip()
        if not name:
            raise InvalidUserNameError("Name cannot be empty")
        return await self._repo.add(User(name, id=user_id))
