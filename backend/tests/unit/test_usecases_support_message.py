import pytest

from application.usecases.support_message_use_case import (
    ChatHistory,
    SupportMessageReadModel,
    SupportMessageUnitOfWork,
    SupportMessageUseCase,
    chat_history,
    support_message_read_model,
)
from domain.entities.support_message import SupportMessage
from domain.exceptions import BusinessLogicException
from infrastructure.database.repositories.support_message_repository import (
    SupportMessageRepository,
)


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
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()


def test_support_message_read_model(support_message_entity):
    sm = support_message_entity()

    sm_read_model = support_message_read_model(sm)

    assert isinstance(sm_read_model, SupportMessageReadModel)


def test_chat_history(support_message_entity):
    message_count = 3
    chat_id = 1
    messages = [
        support_message_entity(id=i, chat_id=chat_id, text=f"{i}_text")
        for i in range(message_count)
    ]

    history = chat_history(messages)

    assert isinstance(history, ChatHistory)
    assert history.chat_id == chat_id
    assert all(m.text == hm.text for m, hm in zip(messages, history.messages))
    assert all(
        f"{m.author_role.upper()}_{m.author_id}" == hm.author
        for m, hm in zip(messages, history.messages)
    )


@pytest.mark.asyncio
async def test_support_message_unit_of_work(session_factory):
    uow = SupportMessageUnitOfWork(session_factory)

    assert uow.session_factory == session_factory
    async with uow:
        assert isinstance(uow.message_repository, SupportMessageRepository)


@pytest.mark.asyncio
async def test_get_and_save_message(session_factory):
    use_case = SupportMessageUseCase(FakeUnitOfWork(session_factory))
    message_id = 1

    with pytest.raises(BusinessLogicException, match="support message not exist"):
        await use_case.get_message(message_id)

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


@pytest.mark.asyncio
async def test_get_chat_history(support_message_entity, session_factory):
    chat_id = 1234
    use_case = SupportMessageUseCase(FakeUnitOfWork(session_factory))

    with pytest.raises(BusinessLogicException, match="no messages or chat not exist"):
        await use_case.get_chat_history(chat_id)

    message_count = 3
    async with use_case.uow:
        for i in range(message_count):
            await use_case.uow.message_repository.persist(
                support_message_entity(id=i, chat_id=chat_id)
            )

    history = await use_case.get_chat_history(chat_id)

    assert isinstance(history, list)
    assert len(history) == message_count
