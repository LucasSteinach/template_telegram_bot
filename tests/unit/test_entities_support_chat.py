from datetime import datetime

from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.entities.user import UserRole


def support_chat():
    return SupportChat(
        id=1,
        user_id=1,
        topic="test_topic",
    )


def test_assign_operator():
    chat = support_chat()
    operator_id = 2

    assert chat.operator_id is None
    assert chat.status == ChatStatus.CREATED

    chat.assign_operator(operator_id)

    assert chat.operator_id == operator_id
    assert chat.status == ChatStatus.ACTIVE


def test_waiting():
    chat = support_chat()

    chat.waiting()

    assert chat.status == ChatStatus.WAITING


def test_active():
    chat = support_chat()

    chat.active()

    assert chat.status == ChatStatus.ACTIVE


def test_close_by_user():
    chat = support_chat()
    user_id, user_role = 1, UserRole.USER

    chat.close(user_id, user_role)

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == "user"


def test_close_by_operator():
    chat = support_chat()
    operator_id, operator_role = 2, UserRole.OPERATOR
    chat.assign_operator(operator_id)

    chat.close(operator_id, operator_role)

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == f"{operator_role}:{operator_id}"


def test_close_by_admin():
    chat = support_chat()
    chat.assign_operator(2)
    admin_id, admin_role = 3, UserRole.ADMIN

    chat.close(admin_id, admin_role)

    assert chat.status == ChatStatus.CLOSED
    assert isinstance(chat.closed_at, datetime)
    assert chat.closed_by == f"{admin_role}:{admin_id}"


def test_close_by_wrong_user():
    chat = support_chat()
    wrong_user_id, user_role = 4, UserRole.USER

    chat.close(wrong_user_id, user_role)

    assert chat.closed_by is None
