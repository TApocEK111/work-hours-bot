from aiogram.utils.keyboard import ReplyKeyboardBuilder


def clockinout_reply_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="/clockin")
    builder.button(text="/clockout")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)
