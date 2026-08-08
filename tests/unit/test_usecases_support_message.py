from __future__ import annotations

import pytest

from src.application.use_cases.support_message_use_case import SupportMessageUseCase
from src.domain.entities.support_message import SupportMessage
from src.domain.repositories.support_message_repository import (
    BaseSupportMessageRepository,
)


class FakeSupportMessageRepository(BaseSupportMessageRepository):
    def __init__(self) -> None:
        self.storage: dict[int, SupportMessage] = {}

    async def get_message(self, message_id: int) -> SupportMessage | None:
        return self.storage.get(message_id)

    async def get_messages_by_chat(self, chat_id: int) -> list[SupportMessage]:
        return [
            message for _, message in self.storage.items() if message.chat_id == chat_id
        ]

    async def persist(self, message: SupportMessage) -> SupportMessage:
        self.storage.update({message.id: message})
        return message


@pytest.mark.asyncio
async def test_get_and_save_message():
    repository = FakeSupportMessageRepository()
    use_case = SupportMessageUseCase(repository)
    message_id = 1

    support_message = await use_case.get_message(message_id)
    assert support_message is None

    dto = SupportMessage(
        id=message_id, chat_id=10, author_id=20, author_role="user", text="message_text"
    )

    support_message = await use_case.save_message(
        chat_id=dto.chat_id,
        author_id=dto.author_id,
        author_role=dto.author_role,
        text=dto.text,
        id_=dto.id,
    )

    assert isinstance(support_message, SupportMessage)

    support_message = await use_case.get_message(message_id)

    assert isinstance(support_message, SupportMessage)
