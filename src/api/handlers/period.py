from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

from application.services.session import SessionService

router = Router(name="period")


@router.message(Command("today"))
async def cmd_today(message: Message, session_service: SessionService):
    if message.from_user:
        sessions = await session_service.get_today_sessions_by_user(
            message.from_user.id
        )
        duration = session_service.sum_duration(sessions)
        await message.answer(f"Today you've worked for {str(duration)}")


@router.message(Command("thisweek"))
async def cmd_thisweek(message: Message, session_service: SessionService):
    if message.from_user:
        sessions = await session_service.get_this_week_sessions_by_user(
            message.from_user.id
        )
        duration = session_service.sum_duration(sessions)
        await message.answer(f"This week you've worked for {str(duration)}")


@router.message(Command("thismonth"))
async def cmd_thisomonth(message: Message, session_service: SessionService):
    if message.from_user:
        sessions = await session_service.get_this_month_sessions_by_user(
            message.from_user.id
        )
        duration = session_service.sum_duration(sessions)
        await message.answer(f"This month you've worked for {str(duration)}")
