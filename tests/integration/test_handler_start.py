from unittest.mock import ANY, AsyncMock, patch

import pytest
from aiogram.exceptions import TelegramBadRequest

from src.infrastructure.telegram.handlers.start import handle_start
from src.infrastructure.telegram.keyboards.menu_constants import MENU


@pytest.mark.asyncio
async def test_handler_start_first_time(
    container, session, session_factory, message, user
):
    message.answer = AsyncMock()
    container.redis_storage.get_main_menu_message_data = AsyncMock(return_value={})
    container.redis_storage.set_main_menu_message_data = AsyncMock()

    with patch(
        "src.infrastructure.telegram.handlers.start.delete_messages",
        new_callable=AsyncMock,
    ) as delete_mock:
        await handle_start(message, container)

    delete_mock.assert_awaited_once_with(message, [message.message_id])
    message.answer.assert_awaited_once_with(
        f"Hi, {user.full_name}!",
        reply_markup=ANY,
    )
    container.redis_storage.set_main_menu_message_data.assert_awaited_once()


@pytest.mark.asyncio
async def test_handler_start_menu_exists(
    container, session, session_factory, message, user
):
    message.answer = AsyncMock()
    container.redis_storage.get_main_menu_message_data = AsyncMock(
        return_value={
            "message_id": 123,
            "message_text": MENU.message_text,
        }
    )

    with (
        patch(
            "src.infrastructure.telegram.handlers.start.delete_messages",
            new_callable=AsyncMock,
        ) as delete_mock,
        patch(
            "src.infrastructure.telegram.handlers.start.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        await handle_start(message, container)

    message.answer.assert_awaited_once()
    delete_mock.assert_awaited_once_with(message, ANY)


@pytest.mark.asyncio
async def test_handler_start_different_menu_messages(
    container, session, session_factory, message, user
):
    message.answer = AsyncMock()
    message.bot = AsyncMock()
    message.bot.edit_message_text = AsyncMock()
    container.redis_storage.get_main_menu_message_data = AsyncMock(
        return_value={
            "message_id": 123,
            "message_text": "different_text",
        }
    )
    container.redis_storage.set_main_menu_message_data = AsyncMock()

    with patch(
        "src.infrastructure.telegram.handlers.start.delete_messages",
        new_callable=AsyncMock,
    ) as delete_mock:
        await handle_start(message, container)

    assert message.answer.await_count == 0
    message.bot.edit_message_text.assert_awaited_once()
    container.redis_storage.set_main_menu_message_data.assert_awaited_once_with(
        message.from_user.id, ANY
    )
    delete_mock.assert_awaited_once_with(message, [message.message_id])


@pytest.mark.asyncio
async def test_handler_start_bad_request(
    container, session, session_factory, message, user
):
    container.redis_storage.get_main_menu_message_data = AsyncMock(
        return_value={
            "message_id": 123,
            "message_text": "different_text",
        }
    )
    message.bot = AsyncMock()
    message.bot.edit_message_text = AsyncMock()
    message.bot.edit_message_text.side_effect = TelegramBadRequest(
        method="editMessageText", message="Bad Request"
    )

    with (
        patch(
            "src.infrastructure.telegram.handlers.start.delete_messages",
            new_callable=AsyncMock,
        ) as delete_mock,
        patch("src.infrastructure.telegram.handlers.start.logger") as logger_mock,
    ):
        await handle_start(message, container)

    message.bot.edit_message_text.assert_awaited_once()
    logger_mock.debug.assert_called_once()
    delete_mock.assert_awaited_once_with(message, [message.message_id])
