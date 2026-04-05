from abc import ABC, abstractmethod

from domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def add(self, user: User) -> bool: ...
