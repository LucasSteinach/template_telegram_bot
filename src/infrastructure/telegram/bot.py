from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.container import Container
from src.infrastructure.config.settings import Settings
from src.infrastructure.telegram.handlers import register_all_routers
from src.infrastructure.telegram.middlewares.container_middleware import (
    ContainerMiddleware,
)


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(container: Container) -> Dispatcher:
    dp = Dispatcher()
    dp.update.outer_middleware(ContainerMiddleware(container))
    register_all_routers(dp)
    print(dp.sub_routers)
    return dp
