from datetime import datetime, timezone

import pytest

from src.domain.entities.support_chat import ChatStatus
from src.infrastructure.database.models import SupportChatModel, SupportMessageModel


@pytest.fixture
def support_message_instance():
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
        return SupportMessageModel(**data)

    return create


@pytest.fixture
def support_chat_instance():
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
        return SupportChatModel(**data)

    return create
