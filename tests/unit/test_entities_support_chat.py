from datetime import datetime

from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.entities.user import UserRole


def support_chat():
    return SupportChat(
        id=1,
        telegram_id=12341234,
        user_id=1,
        topic="test_topic",
    )


def test_assign_operator():
    chat = support_chat()
    operator_id = 2

    assert chat.operator_id is None
    assert chat.status == ChatStatus.CREATED

    last_activity_at = chat.last_activity_at
    assert last_activity_at is not None

    chat.assign_operator(operator_id)

    assert chat.operator_id == operator_id
    assert chat.last_activity_at > last_activity_at


def test_set_waiting():
    chat = support_chat()

    chat.set_waiting()

    assert chat.status == ChatStatus.WAITING


def test_close_by_user():
    chat = support_chat()

    chat.close_by_user()

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == "user"


def test_close_by_operator():
    chat = support_chat()
    operator_id, operator_role = 2, UserRole.OPERATOR

    chat.close_by_operator(operator_id, operator_role)

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == f"{operator_role}:{operator_id}"
