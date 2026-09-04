import pytest

from domain.entities.operator import Operator
from domain.entities.support_chat import SupportChat
from domain.entities.support_message import SupportMessage
from domain.rules.operator_rules import OperatorExist
from domain.rules.support_chat_rules import (
    ChatIsNotClosed,
    IsOperator,
    SupportChatExist,
    UserOwnChat,
    WaitingAfterCreation,
)
from domain.rules.support_message_rules import ChatHasMessages, SupportMessageExist

operator = Operator(id=1, email="test@test.com", password="12341234", is_active=True)
support_message = SupportMessage(chat_id=1, author_id=1, author_role="str", text="str")
support_chat = SupportChat(user_id=1, telegram_id=12341234)


@pytest.mark.parametrize(
    "rule_class, init_kwargs, expected_violated",
    [
        (OperatorExist, {"operator": operator}, False),
        (OperatorExist, {"operator": None}, True),
        (SupportMessageExist, {"message": support_message}, False),
        (SupportMessageExist, {"message": None}, True),
        (ChatHasMessages, {"messages": [support_message]}, False),
        (ChatHasMessages, {"messages": []}, True),
        (SupportChatExist, {"chat": support_chat}, False),
        (SupportChatExist, {"chat": None}, True),
        (UserOwnChat, {"owner_id": 1, "user_id": 1}, False),
        (UserOwnChat, {"owner_id": 1, "user_id": 2}, True),
        (ChatIsNotClosed, {"status": ""}, False),
        (ChatIsNotClosed, {"status": "closed"}, True),
        (WaitingAfterCreation, {"status": "created"}, False),
        (WaitingAfterCreation, {"status": "waiting"}, True),
        (IsOperator, {"role": "operator"}, False),
        (IsOperator, {"role": "user"}, True),
    ],
    ids=[
        "OperatorExist OK",
        "OperatorExist FAILED",
        "SupportMessageExist OK",
        "SupportMessageExist FAILED",
        "ChatHasMessages OK",
        "ChatHasMessages FAILED",
        "SupportChatExist OK",
        "SupportChatExist FAILED",
        "UserOwnChat OK",
        "UserOwnChat FAILED",
        "ChatIsNotClosed OK",
        "ChatIsNotClosed FAILED",
        "WaitingAfterCreation OK",
        "WaitingAfterCreation FAILED",
        "IsOperator OK",
        "IsOperator FAILED",
    ],
)
def test_business_rules(rule_class, init_kwargs, expected_violated):
    rule = rule_class(**init_kwargs)

    assert rule.is_violated() == expected_violated
