from unittest.mock import AsyncMock, ANY, MagicMock

import pytest
from sqlalchemy import select

from src.container import Container
from src.infrastructure.database.models import UserModel
from src.infrastructure.telegram import bot as b
from src.infrastructure.telegram.handlers.start import handle_start
from src.infrastructure.telegram.middlewares.container_middleware import ContainerMiddleware


@pytest.mark.asyncio
async def test_bot(
    session, session_factory, message, user
):
    fake_settings = MagicMock()
    fake_settings.bot_token = "123:test"

    bot = b.create_bot(fake_settings)

    assert bot.token == "123:test"

    container = Container(
        session_factory=session_factory
    )
    dispatcher = b.create_dispatcher(container)
    middlewares = dispatcher.update.outer_middleware._middlewares

    assert dispatcher is not None
    assert any(

        isinstance(middleware, ContainerMiddleware)

        for middleware in middlewares

    )


@pytest.mark.asyncio
async def test_handler_start(
    session, session_factory, message, user
):
    container = Container(
        session_factory=session_factory
    )

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
