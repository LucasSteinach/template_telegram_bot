from unittest.mock import AsyncMock, patch

import pytest
from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.handlers.menu import menu_handler
from src.infrastructure.telegram.keyboards.inline_keyboard import MenuCallback


def test_handlers_init():
    fake_router = Router(name="test")
    with patch(
        "src.infrastructure.telegram.handlers.get_all_routers",
        return_value=[fake_router],
    ):
        dp = Dispatcher()
        assert len(dp.sub_routers) == 0

        register_routers(dp)

        routes_name = [x.name for x in dp.sub_routers]

        assert "test" in routes_name


@pytest.mark.asyncio
async def test_handlers_menu(callback):
    callback_data = MenuCallback(path="root")
    with patch(
        "src.infrastructure.telegram.handlers.menu.render_menu",
        new_callable=AsyncMock,
    ) as mock_render:
        await menu_handler(callback, callback_data)

    callback.answer.assert_awaited_once()
    mock_render.assert_awaited_once_with(
        callback.message,
        "root",
    )
