import pytest

from application.services.auth import AuthService
from application.usecases.operator_use_case import (
    OperatorUnitOfWork,
    OperatorUseCase,
)
from application.usecases.support_chat_use_case import (
    SupportChatUnitOfWork,
    SupportChatUseCase,
)
from application.usecases.support_message_use_case import (
    SupportMessageUnitOfWork,
    SupportMessageUseCase,
)
from application.usecases.user_use_case import UserUnitOfWork, UserUseCase
from container import Container


@pytest.mark.asyncio
async def test_container(session, settings):
    container = Container(settings)

    user_uow = container.user_uow()
    assert isinstance(user_uow, UserUnitOfWork)

    user_uc = container.user_uc()
    assert isinstance(user_uc, UserUseCase)

    operator_uow = container.operator_uow()
    assert isinstance(operator_uow, OperatorUnitOfWork)

    operator_uc = container.operator_uc()
    assert isinstance(operator_uc, OperatorUseCase)

    support_chat_uow = container.support_chat_uow()
    assert isinstance(support_chat_uow, SupportChatUnitOfWork)

    support_chat_uc = container.support_chat_uc()
    assert isinstance(support_chat_uc, SupportChatUseCase)

    support_message_uow = container.support_message_uow()
    assert isinstance(support_message_uow, SupportMessageUnitOfWork)

    support_message_uc = container.support_message_uc()
    assert isinstance(support_message_uc, SupportMessageUseCase)

    auth_service = container.auth_service()
    assert isinstance(auth_service, AuthService)
