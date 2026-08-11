from datetime import datetime, timezone

import pytest

from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.entities.support_message import SupportMessage
from src.domain.entities.user import User


@pytest.fixture
def user_entity():
    def create(**kwargs):
        data = {
            "id": 1,
            "username": "test_user",
            "full_name": "Test User",
            "role": "user",
            "created_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return User(**data)

    return create


@pytest.fixture
def support_message_entity():
    def create(**kwargs):
        data = {
            "id": 1,
            "chat_id": 2,
            "author_id": 3,
            "author_role": "user",
            "text": "test_text",
            "created_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return SupportMessage(**data)

    return create


@pytest.fixture
def support_chat_entity():
    def create(**kwargs):
        data = {
            "id": 1,
            "user_id": 2,
            "topic": None,
            "operator_id": None,
            "status": ChatStatus.CREATED,
            "created_at": datetime.now(tz=timezone.utc),
            "closed_at": None,
            "closed_by": None,
            "last_activity_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return SupportChat(**data)

    return create
