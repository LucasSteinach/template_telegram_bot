from unittest.mock import AsyncMock, call, patch

import pytest
from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.handlers.menu import menu_handler, render_menu
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
async def test_handlers_menu(message):
    callback = AsyncMock()
    callback.message = message
    callback.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
    callback_data = MenuCallback(path="root")

    await menu_handler(callback, callback_data)
    callback.answer.assert_called_once()

    await render_menu(message, "option_1")
    await render_menu(message, "wrong_path")
    await render_menu(message, "option_2")

    message.edit_text.assert_has_calls(
        [call("Main menu"), call("Menu 'Option 1'"), call("Menu 'Option 2'")]
    )
    message.edit_reply_markup.await_count = 3
