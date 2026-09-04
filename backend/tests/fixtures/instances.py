from datetime import datetime, timezone

import pytest

from domain.entities.support_chat import ChatStatus
from infrastructure.database.models import (
    OperatorModel,
    SupportChatModel,
    SupportMessageModel,
    UserModel,
)


@pytest.fixture
def user_instance():
    def create(**kwargs):
        data = {
            "id": 12341234,
            "username": "test_user",
            "full_name": "Test User",
            "created_at": datetime.now(tz=timezone.utc),
            "role": "user",
        }
        data.update(kwargs)
        return UserModel(**data)

    return create


@pytest.fixture
def operator_instance():
    def create(**kwargs):
        data = {
            "id": 12341234,
            "email": "test@test.com",
            "password": "test_password",
            "is_active": True,
            "role": "operator",
        }
        data.update(kwargs)
        return OperatorModel(**data)

    return create


@pytest.fixture
def support_message_instance():
    def create(**kwargs):
        data = {
            "id": 1,
            "chat_id": 1,
            "author_id": 3,
            "author_role": "user",
            "text": "test_text",
            "created_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return SupportMessageModel(**data)

    return create


@pytest.fixture
def support_chat_instance():
    def create(**kwargs):
        data = {
            "id": 1,
            "telegram_id": 12341234,
            "user_id": 2,
            "topic": "topic",
            "operator_id": None,
            "status": ChatStatus.CREATED,
            "created_at": datetime.now(tz=timezone.utc),
            "closed_at": None,
            "closed_by": None,
            "last_activity_at": datetime.now(tz=timezone.utc),
        }
        data.update(kwargs)
        return SupportChatModel(**data)

    return create
