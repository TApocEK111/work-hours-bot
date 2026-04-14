from aiogram.filters.callback_data import CallbackData


class PeriodCallback(CallbackData, prefix="period"):
    action: str
    original_command: str
