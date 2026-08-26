import asyncio
import logging

from src.config import settings
from src.container import Container
from src.infrastructure.telegram.bot import (
    create_bot,
    create_dispatcher,
)


async def main() -> None:
    logging.basicConfig(level=settings.log_level)

    container = Container(settings)
    bot = create_bot(settings)
    dp = create_dispatcher(container, settings)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await container.redis_storage.disconnect()
        await container.engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
