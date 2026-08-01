from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.infrastructure.config.settings import Settings
from src.infrastructure.telegram import bot as tg_bot
from src.infrastructure.telegram.keyboards.dto import MenuItem


@pytest.fixture
def settings():
    return Settings(
        bot_token="123:test",
        database_url="sqlite+aiosqlite:///:memory:",
        log_level="DEBUG",
        fsm_storage="",
        redis_url=None,
    )


@pytest.fixture
def bot(settings):
    fake_settings = MagicMock()
    fake_settings.bot_token = "123:test"

    b = tg_bot.create_bot(fake_settings)
    return b


@pytest.fixture
def user():
    return User(
        id=123, is_bot=False, first_name="User", last_name="Name", username="Test User"
    )


@pytest.fixture
def chat():
    return Chat(
        id=4321,
        type="private",  # also possible 'group', 'supergroup' or 'channel'
    )


@pytest.fixture
def message(user, chat):
    """mock for Message
    message_id=1,
    date=d.datetime.now(),
    chat=chat,
    from_user=user,
    """
    message = AsyncMock(spec=Message)

    message.id = 1
    message.from_user = user
    message.chat = chat

    return message


@pytest.fixture
def callback(message):
    callback = MagicMock()
    callback.message = message
    callback.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
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
