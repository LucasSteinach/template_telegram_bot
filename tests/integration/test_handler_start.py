from unittest.mock import ANY, AsyncMock

import pytest
from sqlalchemy import select

from src.infrastructure.database.models import UserModel
from src.infrastructure.telegram.handlers.start import handle_start


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
