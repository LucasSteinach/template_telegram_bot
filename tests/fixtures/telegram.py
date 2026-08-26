from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from aiogram.types import Chat
from aiogram.types import User as TelegramUser

from src.config import Settings
from src.domain.entities.user import User, UserRole
from src.infrastructure.telegram import bot as tg_bot
from src.infrastructure.telegram.menu.constants import MenuItem


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
        db_user="db_user",
        db_password="db_password",
        db_host="db_host",
        db_port="1234",
        db_name="db_name",
        log_level="DEBUG",
        support_user="12345:@test_support_user",
        fsm_storage="redis",
        redis_url="redis://localhost:6379",
        jwt_secret="",
        access_exp_sec=100,
        refresh_exp_sec=500,
    )


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
        id=123,
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
