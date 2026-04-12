from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from domain.models.user import User
from domain.repositories.user import UserRepository
from infrastructure.db.models import UserModel
from infrastructure.repositories.async_base import BaseAsyncAlchemyRepository


class SQLiteUserRepository(UserRepository, BaseAsyncAlchemyRepository):
    """Async SQLAlchemy SQLite3 User repository"""

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(model.name, id=model.id)

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(name=user.name, id=user.id)

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self._db.execute(query)
        user_model = result.scalar_one_or_none()
        if not user_model:
            return None
        return self._to_domain(user_model)

    async def add(self, user: User) -> bool:
        new_user = self._to_model(user)
        self._db.add(new_user)
        try:
            await self._db.flush()
            return True
        except IntegrityError:
            return False
