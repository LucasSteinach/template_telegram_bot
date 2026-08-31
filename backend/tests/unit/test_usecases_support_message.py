import pytest

from application.usecases.support_message_use_case import (
    SupportMessageUnitOfWork,
    SupportMessageUseCase,
)
from domain.entities.support_message import SupportMessage
from domain.exceptions import BusinessLogicException


class FakeSupportMessageRepository:
    def __init__(self) -> None:
        self.storage: dict[int, SupportMessage] = {}

    async def find_by_id(self, message_id: int) -> SupportMessage | None:
        return self.storage.get(message_id)

    async def get_all_by_chat_id(self, chat_id: int) -> list[SupportMessage]:
        return [
            message for _, message in self.storage.items() if message.chat_id == chat_id
        ]

    async def persist(self, message: SupportMessage) -> SupportMessage:
        self.storage.update({message.id: message})
        return message


class FakeUnitOfWork(SupportMessageUnitOfWork):
    def __init__(self, session_factory=None) -> None:
        super().__init__(session_factory)

        self.message_repository: FakeSupportMessageRepository = (
            FakeSupportMessageRepository()
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_get_and_save_message():
    use_case = SupportMessageUseCase(FakeUnitOfWork())
    message_id = 1

    with pytest.raises(BusinessLogicException, match="support message not exist"):
        await use_case.get_message.__wrapped__(use_case, message_id)

    dto = SupportMessage(
        id=message_id, chat_id=10, author_id=20, author_role="user", text="message_text"
    )

    support_message = await use_case.save_message.__wrapped__(
        use_case,
        chat_id=dto.chat_id,
        author_id=dto.author_id,
        author_role=dto.author_role,
        text=dto.text,
        id_=dto.id,
    )

    assert isinstance(support_message, SupportMessage)

    support_message = await use_case.get_message.__wrapped__(use_case, message_id)

    assert isinstance(support_message, SupportMessage)
