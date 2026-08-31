from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from container import Container
from infrastructure.telegram.middlewares import CallbackLockMiddleware
from infrastructure.telegram.middlewares.container_middleware import ContainerMiddleware


@pytest.mark.asyncio
async def test_container_middleware(settings):
    container = Container(settings)
    middleware = ContainerMiddleware(container)

    data = {}
    handler = AsyncMock()
    event = MagicMock()

    await middleware(handler=handler, event=event, data=data)

    handler.assert_awaited_once_with(event, data)
    assert data["container"] is container


@pytest.mark.asyncio
async def test_callback_lock_middleware(telegram_user, message):
    middleware = CallbackLockMiddleware()
    assert len(middleware.processing) == 0

    data = {}
    handler = AsyncMock()
    event = AsyncMock()
    event.from_user.id = telegram_user.id
    event.message.message_id = message.message_id
    event.answer = AsyncMock()

    await middleware(handler, event, data)

    assert len(middleware.processing) == 0
    handler.assert_awaited_once_with(event, data)

    middleware.processing.add((telegram_user.id, message.message_id))
    await middleware(handler, event, data)

    assert handler.await_count == 1
    event.answer.assert_has_awaits(
        [
            call(),
            call("⏳ Processed.."),
        ]
    )
