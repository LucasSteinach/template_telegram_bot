from __future__ import annotations

import pytest

from src.application.usecases.support_chat_use_case import (
    SupportChatUnitOfWork,
    SupportChatUseCase,
)
from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.exceptions import BusinessLogicException


class FakeSupportChatRepository:
    def __init__(self) -> None:
        self.storage: dict[int, SupportChat] = {}

    async def find_by_id(self, chat_id: int) -> SupportChat | None:
        return self.storage.get(chat_id)

    async def get_all_active_chats(self) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.status != ChatStatus.CLOSED
        ]

    async def get_all_by_user_id(self, user_id: int) -> list[SupportChat]:
        return [chat for _, chat in self.storage.items() if chat.user_id == user_id]

    async def get_all_closed_chats(self) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.status == ChatStatus.CLOSED
        ]

    async def persist(self, chat: SupportChat) -> SupportChat:
        self.storage.update({chat.id: chat})
        return chat


class FakeUnitOfWork(SupportChatUnitOfWork):
    def __init__(self, session_factory=None) -> None:
        super().__init__(session_factory)

        self.chat_repository: FakeSupportChatRepository = FakeSupportChatRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_create_chat(user):
    use_case = SupportChatUseCase(FakeUnitOfWork())
    chat_id = 1

    chat = await use_case.create_chat.__wrapped__(use_case, user.id, chat_id)

    assert isinstance(chat, SupportChat)
    assert chat.user_id == user.id


@pytest.mark.asyncio
async def test_close_chat(user):
    use_case = SupportChatUseCase(FakeUnitOfWork())
    chat_id = 1

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.close_chat.__wrapped__(use_case, chat_id, None)

    chat = await use_case.create_chat.__wrapped__(use_case, user.id, chat_id)
    await use_case.close_chat.__wrapped__(use_case, chat.id, user)

    assert isinstance(chat, SupportChat)
    assert chat.status == ChatStatus.CLOSED
