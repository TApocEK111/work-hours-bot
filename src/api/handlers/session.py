from aiogram import F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.filters.command import Command
from aiogram.types import ErrorEvent, Message

from application.exceptions import (
    AlreadyClockedInError,
    NoActiveSessionError,
    NoUserError,
)
from application.services.session import SessionService

router = Router(name="session")


@router.error(ExceptionTypeFilter(NoUserError), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message):
    await message.answer("You are not authorized to do it!")


@router.message(Command("clockin"))
async def cmd_clockin(message: Message, session_service: SessionService):
    if message.from_user:
        try:
            await session_service.clock_in_user(message.from_user.id)
            await message.answer("Clocked in.")
        except AlreadyClockedInError:
            await message.answer("Already clocked in.")


@router.message(Command("clockout"))
async def cmd_clockout(message: Message, session_service: SessionService):
    if message.from_user:
        try:
            await session_service.clock_out_user(message.from_user.id)
            await message.answer("Clocked out.")
        except NoActiveSessionError:
            await message.answer("No active session to clock out from.")
