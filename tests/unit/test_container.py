import pytest

from src.application.use_cases.support_chat_use_case import SupportChatUseCase
from src.application.use_cases.support_message_use_case import SupportMessageUseCase
from src.application.use_cases.user_use_case import UserUseCase
from src.container import Container


@pytest.mark.asyncio
async def test_container(session, settings):
    container = Container(settings)

    user_uc = container.user_uc(session)
    assert isinstance(user_uc, UserUseCase)

    support_chat_uc = container.support_chat_uc(session)
    assert isinstance(support_chat_uc, SupportChatUseCase)

    support_message_uc = container.support_message_uc(session)
    assert isinstance(support_message_uc, SupportMessageUseCase)
