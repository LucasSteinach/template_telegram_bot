from unittest.mock import ANY, AsyncMock, call, patch

import pytest
from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.handlers.main_menu import (
    handle_option_1,
    handle_option_2,
)


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
async def test_handler_main_menu(container):
    callback = AsyncMock()
    callback.answer = AsyncMock()
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()

    await handle_option_1(callback, container)
    await handle_option_2(callback, container)

    callback.answer.assert_has_calls(
        [
            call("option 1"),
            call("option 2"),
        ]
    )
    callback.message.edit_text.assert_has_calls(
        [
            call(text="option 1 menu", reply_markup=ANY),
            call(text="option 2 menu", reply_markup=ANY),
        ]
    )
