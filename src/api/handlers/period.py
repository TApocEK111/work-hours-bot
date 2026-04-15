from typing import Any, Callable, Coroutine

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message

from api.callback import PeriodCallback
from api.keyboards import refresh_period_inline_keyboard
from application.services.session import SessionService
from domain.models.session import Session

router = Router(name="period")


def _todict(method_name: str, period_name: str) -> dict[str, str]:
    return {"method_name": method_name, "period_name": period_name}


_COMMAND_VARS = {
    "/today": _todict("get_today_sessions_by_user", "Today"),
    "/thisweek": _todict("get_this_week_sessions_by_user", "This week"),
    "/thismonth": _todict("get_this_month_sessions_by_user", "This month"),
}


@router.message(Command("today", "thisweek", "thismonth"))
async def cmd_today(message: Message, session_service: SessionService):
    if not message.text:
        await message.answer("Somehow you've entered command handler without text.")
        return
    if message.from_user:
        period_method: Callable[[int], Coroutine[Any, Any, list[Session]]] = getattr(
            session_service, _COMMAND_VARS[message.text]["method_name"]
        )
        sessions = await period_method(message.from_user.id)
        duration = session_service.sum_duration(sessions)
        await message.answer(
            f"{_COMMAND_VARS[message.text]['period_name']} you've worked for {str(duration)}",
            reply_markup=refresh_period_inline_keyboard(message.text),
        )


@router.callback_query(PeriodCallback.filter(F.action == "refresh"))
async def period_callback_refresh(
    query: CallbackQuery, callback_data: PeriodCallback, session_service: SessionService
):
    if not query.message:
        query.answer("Somehow you've accessed this button outside of the bot dialogue.")
        return
    if query.from_user:
        period_method: Callable[[int], Coroutine[Any, Any, list[Session]]] = getattr(
            session_service,
            _COMMAND_VARS[callback_data.original_command]["method_name"],
        )
        sessions = await period_method(query.from_user.id)
        duration = session_service.sum_duration(sessions)
        try:
            await query.message.edit_text(  # type: ignore
                f"{_COMMAND_VARS[callback_data.original_command]['period_name']} you've worked for {str(duration)}",
                reply_markup=refresh_period_inline_keyboard(
                    callback_data.original_command
                ),
            )
        except TelegramBadRequest:
            await query.answer("Nothing new.")
