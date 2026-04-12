from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from api.dependency import Container
from infrastructure.db.session import get_session


class DIMiddleware(BaseMiddleware):
    def __init__(self, container: Container):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with get_session(self.container.session_maker) as session:
            data["user_service"] = self.container.get_user_service(session)
            data["session_service"] = self.container.get_session_service(session)

            return await handler(event, data)
