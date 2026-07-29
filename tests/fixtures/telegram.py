from unittest.mock import AsyncMock

import pytest
from aiogram.types import Message, Chat, User


@pytest.fixture
def user():
    return User(
        id=123,
        is_bot=False,
        first_name="User",
        last_name="Name",
        username="Test User"
    )


@pytest.fixture
def chat():
    return Chat(
        id=4321,
        type='private',  # also possible 'group', 'supergroup' or 'channel'
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
