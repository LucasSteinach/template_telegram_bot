import pytest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from src.infrastructure.telegram import bot as b
from src.infrastructure.telegram.bot import create_fsm_storage
from src.infrastructure.telegram.middlewares import ContainerMiddleware


def test_create_fsm_storage(settings):
    # none
    storage = create_fsm_storage(settings)

    assert isinstance(storage, MemoryStorage)

    # redis
    settings.fsm_storage = "redis"
    settings.redis_url = "redis://localhost:6379"

    storage = create_fsm_storage(settings)

    assert isinstance(storage, RedisStorage)

    # incorrect fsm
    settings.fsm_storage = "incorrect data"

    storage = create_fsm_storage(settings)

    assert isinstance(storage, MemoryStorage)


@pytest.mark.asyncio
async def test_bot(bot, container, session, session_factory, settings, message, user):
    dispatcher = b.create_dispatcher(container, settings)
    middlewares = dispatcher.update.outer_middleware._middlewares

    assert dispatcher is not None
    assert any(
        isinstance(middleware, ContainerMiddleware) for middleware in middlewares
    )
