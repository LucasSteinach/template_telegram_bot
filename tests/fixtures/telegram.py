from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from aiogram.types import Chat, User

from src.infrastructure.config.settings import Settings
from src.infrastructure.telegram import bot as tg_bot
from src.infrastructure.telegram.keyboards.menu_constants import MenuItem


@pytest.fixture(
    # autouse=True  to check for warnings' source
)
def check_gc():
    import tracemalloc

    tracemalloc.start(10)
    yield
    import gc

    gc.collect()


@pytest.fixture
def settings():
    return Settings(
        bot_token="123:test",
        database_url="sqlite+aiosqlite:///:memory:",
        log_level="DEBUG",
        support_user="12345:@test_support_user",
        fsm_storage="redis",
        redis_url="redis://localhost:6379",
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
    message = Mock()

    message.message_id = 1
    message.text = "test_text"
    message.from_user = user
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
