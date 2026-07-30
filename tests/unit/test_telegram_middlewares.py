from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.container import Container
from src.infrastructure.telegram.middlewares import CallbackLockMiddleware
from src.infrastructure.telegram.middlewares.container_middleware import (
    ContainerMiddleware,
)


@pytest.mark.asyncio
async def test_container_middleware(session):
    session_factory = MagicMock()
    container = Container(session_factory=session_factory)
    middleware = ContainerMiddleware(container)

    data = {}
    handler = AsyncMock()
    event = MagicMock()

    await middleware(handler=handler, event=event, data=data)

    handler.assert_awaited_once_with(event, data)
    assert data["container"] is container


@pytest.mark.asyncio
async def test_callback_lock_middleware(user, message):
    middleware = CallbackLockMiddleware()
    assert len(middleware.processing) == 0

    data = {}
    handler = AsyncMock()
    event = AsyncMock()
    event.from_user.id = user.id
    event.message.message_id = message.id
    event.answer = AsyncMock()

    await middleware(handler, event, data)

    assert len(middleware.processing) == 0
    handler.assert_awaited_once_with(event, data)

    middleware.processing.add((user.id, message.id))
    await middleware(handler, event, data)

    assert handler.await_count == 1
    event.answer.assert_has_awaits(
        [
            call(),
            call("⏳ Processed.."),
        ]
    )
