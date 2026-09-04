from datetime import datetime, timezone

import pytest

from domain.entities.operator import Operator
from domain.entities.support_chat import ChatStatus, SupportChat
from domain.entities.support_message import SupportMessage
from domain.entities.user import User


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
def operator_entity():
    def create(**kwargs):
        data = {
            "id": 12341234,
            "email": "test@test.com",
            "password": "test_password",
            "is_active": True,
            "role": "operator",
        }
        data.update(kwargs)
        return Operator(**data)

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
            "telegram_id": 12341234,
            "user_id": 2,
            "topic": "topic",
            "operator_id": 12341234,
            "status": ChatStatus.CREATED,
            "created_at": datetime.now(tz=timezone.utc),
            "closed_at": None,
            "closed_by": None,
            "last_activity_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return SupportChat(**data)

    return create
