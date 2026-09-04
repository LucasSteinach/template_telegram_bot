import pytest

from application.usecases.support_chat_use_case import (
    SupportChatReadModel,
    SupportChatUnitOfWork,
    SupportChatUseCase,
    support_chat_read_model,
)
from domain.entities.support_chat import ChatStatus, SupportChat
from domain.exceptions import BusinessLogicException
from infrastructure.database.repositories.support_chat_repository import (
    SupportChatRepository,
)


class FakeSupportChatRepository:
    def __init__(self) -> None:
        self.storage: dict[int, SupportChat] = {}

    async def find_by_id(self, chat_id: int) -> SupportChat | None:
        return self.storage.get(chat_id)

    async def get_all_active_chats(self) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.status != ChatStatus.CLOSED
        ]

    async def get_assigned_chats(self, operator_id: int) -> list[SupportChat]:
        return [
            chat for _, chat in self.storage.items() if chat.operator_id == operator_id
        ]

    async def get_all_by_user_id(self, user_id: int) -> list[SupportChat]:
        return [chat for _, chat in self.storage.items() if chat.user_id == user_id]

    async def get_waiting_chats(self) -> list[SupportChat]:
        return [
            chat
            for _, chat in self.storage.items()
            if chat.status == ChatStatus.WAITING
        ]

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
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()


def test_support_chat_read_model(support_chat_entity):
    chat = support_chat_entity()

    read_model = support_chat_read_model(chat)

    assert isinstance(read_model, SupportChatReadModel)
    assert chat.id == read_model.id


@pytest.mark.asyncio
async def test_support_chat_uow(session_factory):
    uow = SupportChatUnitOfWork(session_factory)
    assert uow.session_factory == session_factory

    async with uow:
        assert isinstance(uow.chat_repository, SupportChatRepository)


@pytest.mark.asyncio
async def test_create_chat(user, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1

    chat = await use_case.create_chat(user.id, chat_id)

    assert isinstance(chat, SupportChat)
    assert chat.user_id == user.id


@pytest.mark.asyncio
async def test_get_chat(support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1
    entity = support_chat_entity(id=chat_id)

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.get_chat(chat_id)

    await use_case.uow.chat_repository.persist(entity)

    chat = await use_case.get_chat(chat_id)

    assert isinstance(chat, SupportChat)
    assert chat.id == chat_id


@pytest.mark.asyncio
async def test_get_user_chats(user, support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1
    entity = support_chat_entity(id=chat_id, user_id=user.id)

    no_chats_list = await use_case.get_user_chats(user.id)

    assert no_chats_list == []

    await use_case.uow.chat_repository.persist(entity)

    chats_list = await use_case.get_user_chats(user.id)

    assert len(chats_list) == 1


@pytest.mark.asyncio
async def test_get_assigned_chats(support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    operator_id = 1
    entity = support_chat_entity(id=1, operator_id=operator_id)

    no_chats_list = await use_case.get_assigned_chats(operator_id)

    assert no_chats_list == []

    await use_case.uow.chat_repository.persist(entity)

    chats_list = await use_case.get_assigned_chats(operator_id)

    assert len(chats_list) == 1


@pytest.mark.asyncio
async def test_get_waiting_chats(support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    entity = support_chat_entity(id=1, status="waiting")

    no_chats_list = await use_case.get_waiting_chats()

    assert no_chats_list == []

    await use_case.uow.chat_repository.persist(entity)

    chats_list = await use_case.get_waiting_chats()

    assert len(chats_list) == 1


@pytest.mark.asyncio
async def test_close_chat(user, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.close_chat(chat_id, None)

    chat = await use_case.create_chat(user.id, chat_id)
    await use_case.close_chat(chat.id, user)

    assert isinstance(chat, SupportChat)
    assert chat.status == ChatStatus.CLOSED


@pytest.mark.asyncio
async def test_user_set_waiting_status(user, support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.user_set_waiting_status(chat_id, user, "topic")

    entity = support_chat_entity(user_id=user.id + 1)
    await use_case.uow.chat_repository.persist(entity)

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.user_set_waiting_status(chat_id, user, "topic")

    entity = support_chat_entity(user_id=user.id, status="closed")
    await use_case.uow.chat_repository.persist(entity)

    with pytest.raises(BusinessLogicException, match="chat closed"):
        await use_case.user_set_waiting_status(chat_id, user, "topic")

    entity = support_chat_entity(user_id=user.id, topic=None)
    await use_case.uow.chat_repository.persist(entity)

    chat = await use_case.user_set_waiting_status(chat_id, user, "topic")

    assert isinstance(chat, SupportChat)
    assert chat.topic == "topic"


@pytest.mark.asyncio
async def test_operator_answers(user, support_chat_entity, session_factory):
    use_case = SupportChatUseCase(FakeUnitOfWork(session_factory))
    chat_id = 1

    with pytest.raises(BusinessLogicException, match="chat not exist"):
        await use_case.operator_answers(chat_id, user.id, user.role)

    entity = support_chat_entity(user_id=user.id, operator_id=None, status="closed")
    await use_case.uow.chat_repository.persist(entity)

    with pytest.raises(BusinessLogicException, match="chat closed"):
        await use_case.operator_answers(chat_id, user.id, user.role)

    entity = support_chat_entity(
        user_id=user.id,
        operator_id=None,
    )
    await use_case.uow.chat_repository.persist(entity)

    with pytest.raises(BusinessLogicException, match="user is not an operator"):
        await use_case.operator_answers(chat_id, user.id, user.role)

    chat = await use_case.operator_answers(chat_id, user.id, "operator")

    assert isinstance(chat, SupportChat)
    assert chat.operator_id == user.id
    assert chat.status == "active"
