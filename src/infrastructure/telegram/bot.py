from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.container import Container
from src.infrastructure.config.settings import Settings
from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.middlewares import register_middlewares


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(container: Container) -> Dispatcher:
    dp = Dispatcher()
    register_middlewares(dp, container)
    register_routers(dp)
    return dp
