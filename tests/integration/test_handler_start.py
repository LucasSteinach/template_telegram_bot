from unittest.mock import ANY, AsyncMock

import pytest
from sqlalchemy import select

from src.infrastructure.database.models import UserModel
from src.infrastructure.telegram import bot as b
from src.infrastructure.telegram.handlers.start import handle_start
from src.infrastructure.telegram.middlewares.container_middleware import (
    ContainerMiddleware,
)


@pytest.mark.asyncio
async def test_bot(bot, container, session, session_factory, message, user):
    dispatcher = b.create_dispatcher(container)
    middlewares = dispatcher.update.outer_middleware._middlewares

    assert dispatcher is not None
    assert any(
        isinstance(middleware, ContainerMiddleware) for middleware in middlewares
    )


@pytest.mark.asyncio
async def test_handler_start(container, session, session_factory, message, user):
    message.answer = AsyncMock()

    await handle_start(
        message,
        container,
    )

    message.answer.assert_called_once_with(
        f"Hi, {user.full_name}!",
        reply_markup=ANY,
    )

    async with session as s:
        user = await s.scalar(select(UserModel))

    assert user is not None
    assert user.telegram_id == user.telegram_id
