from datetime import datetime

from domain.entities.support_chat import ChatStatus
from domain.entities.user import UserRole


def test_assign_operator(support_chat_entity):
    chat = support_chat_entity(operator_id=None)
    operator_id = 2

    assert chat.status == ChatStatus.CREATED

    last_activity_at = chat.last_activity_at
    assert last_activity_at is not None

    chat.assign_operator(operator_id)

    assert chat.operator_id == operator_id
    assert chat.last_activity_at > last_activity_at


def test_activate(support_chat_entity):
    chat = support_chat_entity()

    chat.activate()

    assert chat.status == ChatStatus.ACTIVE


def test_set_waiting(support_chat_entity):
    chat = support_chat_entity()

    chat.set_waiting()

    assert chat.status == ChatStatus.WAITING


def test_close_by_user(support_chat_entity):
    chat = support_chat_entity()

    chat.close_by_user()

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == "user"


def test_close_by_operator(support_chat_entity):
    chat = support_chat_entity()
    operator_id, operator_role = 2, UserRole.OPERATOR

    chat.close_by_operator(operator_id, operator_role)

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == f"{operator_role}:{operator_id}"
