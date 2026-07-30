import asyncio
import logging

from src.container import Container
from src.infrastructure.config.settings import settings
from src.infrastructure.database.db import async_session_factory
from src.infrastructure.telegram.bot import create_bot, create_dispatcher, create_fsm_storage


async def main() -> None:
    logging.basicConfig(level=settings.log_level)

    container = Container(session_factory=async_session_factory)
    bot = create_bot(settings)
    dp = create_dispatcher(container, create_fsm_storage(settings))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
