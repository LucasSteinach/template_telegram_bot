import asyncio
import logging

from src.config import settings
from src.container import Container
from src.infrastructure.telegram.bot import (
    create_bot,
    create_dispatcher,
)
from src.infrastructure.telegram.handlers.operator import handle_support_message


async def main() -> None:
    logging.basicConfig(level=settings.log_level)

    container = Container(settings)
    rabbitmq = container.rabbitmq
    await rabbitmq.connect()

    bot = create_bot(settings)
    dp = create_dispatcher(container, settings)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(dp.start_polling(bot, handle_signals=False))
            tg.create_task(
                rabbitmq.consume(
                    "support_messages",
                    lambda **data: handle_support_message(
                        bot=bot,
                        dispatcher=dp,
                        **data,
                    ),
                )
            )
    finally:
        await rabbitmq.close()
        await container.redis_storage.disconnect()
        await container.engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
