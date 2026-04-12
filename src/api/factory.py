from aiogram import Bot, Dispatcher

from api.handlers import setup_routers


def create_bot(token: str) -> Bot:
    return Bot(token)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    setup_routers(dp)
    return dp
