from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from api.callback import PeriodCallback


def clockinout_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="/clockin")
    builder.button(text="/clockout")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def refresh_period_inline_keyboard(command: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄 Refresh",
        callback_data=PeriodCallback(action="refresh", original_command=command).pack(),
    )
    return builder.as_markup()
