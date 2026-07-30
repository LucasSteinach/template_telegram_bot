from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.fsm.storage.redis import RedisStorage

from src.container import Container
from src.infrastructure.config.settings import Settings
from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.middlewares import register_middlewares


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_fsm_storage(settings: Settings):
    if not settings.fsm_storage:
        return MemoryStorage
    if settings.fsm_storage == "redis":
        return RedisStorage.from_url(settings.fsm_storage_url)
    if settings.fsm_storage == "mongodb":
        return MongoStorage.from_url(settings.fsm_storage_url)
    return MemoryStorage


def create_dispatcher(container: Container, fsm_storage: MemoryStorage | RedisStorage | MongoStorage) -> Dispatcher:
    dp = Dispatcher(storage=fsm_storage)
    register_middlewares(dp, container)
    register_routers(dp)
    return dp
