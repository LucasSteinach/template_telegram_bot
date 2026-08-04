from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest
from aiogram import Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest

from src.infrastructure.telegram.callbacks import MenuCallback
from src.infrastructure.telegram.fsm_states import InputDataState
from src.infrastructure.telegram.handlers import register_routers
from src.infrastructure.telegram.handlers.actions.helpers import (
    add_messages_to_cleanup,
    delete_messages,
)
from src.infrastructure.telegram.handlers.actions.input_data import (
    input_data_handler,
    process_input,
)
from src.infrastructure.telegram.handlers.fallback import delete_unhandled_messages
from src.infrastructure.telegram.handlers.menu import menu_handler


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
async def test_menu_handler(callback):
    callback_data = MenuCallback(path="root")
    with patch("src.infrastructure.telegram.handlers.menu.render_menu") as mock_render:
        await menu_handler(callback, callback_data)

    callback.answer.assert_awaited_once()
    mock_render.assert_awaited_once_with(
        callback.message,
        "root",
    )


@pytest.mark.asyncio
async def test_fallback_handler(message):
    message.delete = AsyncMock()

    await delete_unhandled_messages(message)

    message.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_actions_input_data_handler(callback):
    path = "src.infrastructure.telegram.handlers.actions.input_data"
    state = AsyncMock()
    state.set_state = AsyncMock()

    with (
        patch(f"{path}.logger") as logger_mock,
        patch(f"{path}.add_messages_to_cleanup") as add_message_to_cleanup_mock,
    ):
        await input_data_handler(callback, state)

    logger_mock.debug.assert_called_once()
    state.set_state.assert_awaited_once_with(InputDataState.waiting_data)
    callback.message.answer.assert_awaited_once()
    add_message_to_cleanup_mock.assert_awaited_once_with(state, ANY)


@pytest.mark.asyncio
async def test_actions_process_input_handler(message):
    path = "src.infrastructure.telegram.handlers.actions.input_data"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"cleanup_messages": []})
    state.clear = AsyncMock()

    with (
        patch(f"{path}.logger") as logger_mock,
        patch(f"{path}.add_messages_to_cleanup") as add_message_to_cleanup_mock,
        patch(f"{path}.delete_messages") as delete_messages_mock,
        patch(f"{path}.asyncio.sleep") as sleep_mock,
    ):
        await process_input(message, state)

    logger_mock.debug.assert_called_once()
    add_message_to_cleanup_mock.assert_awaited_once_with(state, ANY)
    state.get_data.assert_awaited_once()
    state.clear.assert_awaited_once()
    sleep_mock.assert_awaited_once()
    assert message.answer.await_count == 2
    delete_messages_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_messages_to_cleanup():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"cleanup_messages": []})
    state.update_data = AsyncMock()
    message_ids = [1, 2, 3]

    await add_messages_to_cleanup(state, message_ids)

    state.get_data.assert_awaited_once()
    state.update_data.assert_awaited_once_with(cleanup_messages=[1, 2, 3])


@pytest.mark.asyncio
async def test_delete_messages(message):
    path = "src.infrastructure.telegram.handlers.actions.helpers"
    message.bot = Mock()
    message.bot.delete_message = AsyncMock()
    message_ids = [1, 2, 3]

    await delete_messages(message, message_ids)

    assert message.bot.delete_message.await_count == 3
    assert message.bot.delete_message.await_count == len(message_ids)

    message.bot.delete_message.side_effect = TelegramBadRequest(
        method="BadRequest", message="some_error"
    )

    with patch(f"{path}.logger") as logger_mock:
        await delete_messages(message, message_ids)

    assert logger_mock.debug.call_count == 3
