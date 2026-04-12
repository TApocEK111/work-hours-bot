from aiogram import Bot, Dispatcher


async def start_bot(mode: str, bot: Bot, dispatcher: Dispatcher):
    if mode == "polling":
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)  # pyright: ignore[reportUnknownMemberType]
    else:
        raise NotImplementedError
