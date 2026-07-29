from __future__ import annotations

import pytest

from unittest.mock import AsyncMock, MagicMock

from src.container import Container
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
