import asyncio

from api import start_bot
from api.dependency import Container
from api.factory import create_bot, create_dispatcher
from api.middlewares.di import DIMiddleware
from infrastructure.api_config import BotConfig
from infrastructure.clock import SystemClock
from infrastructure.db.config import DBConfig
from infrastructure.db.engine import create_engine, init_db
from infrastructure.db.session import create_session_maker


async def main():
    db_config = DBConfig()
    engine = create_engine(db_config)
    await init_db(engine)
    session_maker = create_session_maker(engine)
    clock = SystemClock()

    container = Container(session_maker, clock)

    bot_config = BotConfig()
    bot = create_bot(bot_config.bot_token)
    dispatcher = create_dispatcher()

    dispatcher.message.middleware(DIMiddleware(container))
    dispatcher.message.outer_middleware()

    await start_bot(bot_config.deploy_method, bot, dispatcher)


if __name__ == "__main__":
    asyncio.run(main())
