from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

import api.handlers.basic as basic
import api.handlers.period as period
import api.handlers.session as session


def setup_routers(dp: Dispatcher):
    dp.include_router(basic.router)
    dp.include_router(session.router)
    dp.include_router(period.router)


class AuthStatus(StatesGroup):
    waiting_for_password = State()
    logged_in = State()
