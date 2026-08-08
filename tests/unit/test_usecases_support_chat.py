from __future__ import annotations

import pytest

from src.application.use_cases.support_chat_use_case import SupportChatUseCase
from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.repositories.support_chat_repository import BaseSupportChatRepository


class FakeSupportChatRepository(BaseSupportChatRepository):
    def __init__(self) -> None:
        self.storage: dict[int, SupportChat] = {}

    async def get_chat(self, chat_id: int) -> SupportChat | None:
        return self.storage.get(chat_id)

    async def get_active_chats(self) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.status != ChatStatus.CLOSED
        ]

    async def get_chats_by_user(self, user_id: int) -> list[SupportChat]:
        return [chat for _, chat in self.storage.items() if chat.user_id == user_id]

    async def get_closed_chats(self) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.status == ChatStatus.CLOSED
        ]

    async def persist(self, chat: SupportChat) -> SupportChat:
        self.storage.update({chat.id: chat})
        return chat


@pytest.mark.asyncio
async def test_get_and_save_chat(user):
    repository = FakeSupportChatRepository()
    use_case = SupportChatUseCase(repository)
    chat_id = 1

    support_chat = await use_case.get_chat(chat_id)
    assert support_chat is None

    dto = SupportChat(id=chat_id, user_id=user.telegram_id)

    support_chat = await use_case.save_chat(dto)
    assert isinstance(support_chat, SupportChat)

    support_chat = await use_case.get_chat(chat_id=chat_id)

    assert isinstance(support_chat, SupportChat)
    assert support_chat.user_id == user.telegram_id


@pytest.mark.asyncio
async def test_create_chat(user):
    repository = FakeSupportChatRepository()
    use_case = SupportChatUseCase(repository)
    chat_id = 1

    chat = await use_case.create_chat(user.telegram_id, chat_id)

    assert isinstance(chat, SupportChat)
    assert chat.user_id == user.telegram_id


@pytest.mark.asyncio
async def test_close_chat(user):
    repository = FakeSupportChatRepository()
    use_case = SupportChatUseCase(repository)
    chat_id = 1

    chat = await use_case.close_chat(chat_id, None)

    assert chat is None

    await use_case.create_chat(user.telegram_id, chat_id)
    chat = await use_case.close_chat(chat_id, user)

    assert isinstance(chat, SupportChat)
    assert chat.status == ChatStatus.CLOSED
