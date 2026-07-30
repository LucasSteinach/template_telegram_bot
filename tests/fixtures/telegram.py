from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.infrastructure.telegram import bot as tg_bot


@pytest.fixture()
def bot():
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
    message = AsyncMock(spec=Message)

    message.id = 1
    message.from_user = user
    message.chat = chat

    return message
    # mock for Message(
    #     message_id=1,
    #     date=d.datetime.now(),
    #     chat=chat,
    #     from_user=user,
    # )
