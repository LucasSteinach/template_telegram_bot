from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from aiogram.types import Chat
from aiogram.types import User as TelegramUser

from domain.entities.user import User, UserRole
from infrastructure.telegram import bot as tg_bot
from infrastructure.telegram.menu.menu import MenuItem


@pytest.fixture
def bot(settings):
    fake_settings = MagicMock()
    fake_settings.bot_token = "123:test"

    b = tg_bot.create_bot(fake_settings)
    return b


@pytest.fixture
def telegram_user():
    return TelegramUser(
        id=123,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="Test User",
        role=UserRole.USER,
    )


@pytest.fixture
def user():
    return User(
        id=12341234,
        username="Test User",
        full_name="Fullname Test User",
        created_at=datetime(2025, 8, 12, tzinfo=timezone.utc),
        role=UserRole.USER,
    )


@pytest.fixture
def chat():
    return Chat(
        id=4321,
        type="private",  # also possible 'group', 'supergroup' or 'channel'
    )


@pytest.fixture
def message(telegram_user, chat):
    message = Mock()

    message.message_id = 1
    message.text = "test_text"
    message.from_user = telegram_user
    message.chat = chat

    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()

    return message


@pytest.fixture
def callback(message):
    callback = Mock()
    callback.message = message
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def menu_item():
    return MenuItem(
        id="root",
        message_text="message text",
        button_text="button text",
        type="menu",
        children=[
            MenuItem(
                id="child_1",
                message_text="message 1",
                button_text="button 1",
                type="menu",
            ),
            MenuItem(
                id="child_2",
                message_text="message 2",
                button_text="button 2",
                type="action",
            ),
        ],
    )
