import logging
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.usecases.base_use_case import AsyncBaseUnitOfWork
from src.domain.entities.support_chat import SupportChat
from src.domain.entities.user import User
from src.domain.rules.rules import check_business_rule
from src.domain.rules.support_chat_rules import (
    ChatIsNotClosed,
    IsOperator,
    SupportChatExist,
    UserOwnChat,
    WaitingAfterCreation,
)
from src.infrastructure.database.repositories.support_chat_repository import (
    SupportChatRepository,
)
from src.infrastructure.database.sqlalchemy.transaction import async_transaction

logger = logging.getLogger(__name__)


class SupportChatReadModel(BaseModel):
    id: int
    topic: str
    user_id: int
    created_at: datetime


def support_chat_read_model(c: SupportChat):
    return SupportChatReadModel(
        id=c.id,
        topic=c.topic,
        user_id=c.user_id,
        created_at=c.created_at,
    )


class SupportChatUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self):
        await super().__aenter__()

        self.chat_repository: SupportChatRepository = SupportChatRepository(
            self.session
        )


class SupportChatUseCase:
    def __init__(self, uow: SupportChatUnitOfWork) -> None:
        self.uow: SupportChatUnitOfWork = uow

    async def _get_chat(self, chat_id: int) -> SupportChat | None:
        return await self.uow.chat_repository.find_by_id(chat_id)

    @async_transaction(read_only=True)
    async def get_chat(self, chat_id: int) -> SupportChat:
        support_chat = await self._get_chat(chat_id)
        check_business_rule(SupportChatExist(chat=support_chat))

        return support_chat

    @async_transaction(read_only=True)
    async def get_assigned_chats(self, operator_id: int) -> list[SupportChat]:
        chats = await self.uow.chat_repository.get_assigned_chats(operator_id)
        return chats

    @async_transaction()
    async def create_chat(self, user_id: int, id_: int | None = None) -> SupportChat:
        return await self.uow.chat_repository.persist(
            SupportChat(id=id_, user_id=user_id)
        )

    @async_transaction()
    async def user_set_awaiting_status(
        self, chat_id: int, user: User, topic: str
    ) -> SupportChat | None:
        support_chat = await self._get_chat(chat_id)
        check_business_rule(SupportChatExist(chat=support_chat))
        check_business_rule(UserOwnChat(owner_id=support_chat.user_id, user_id=user.id))
        check_business_rule(ChatIsNotClosed(status=support_chat.status))
        check_business_rule(WaitingAfterCreation(status=support_chat.status))

        support_chat.set_waiting()
        if support_chat.topic is None:
            support_chat.topic = topic

        return await self.uow.chat_repository.persist(support_chat)

    @async_transaction()
    async def assign_operator(
        self, chat_id: int, user_id: int, role: str
    ) -> SupportChat | None:
        support_chat = await self._get_chat(chat_id)
        check_business_rule(SupportChatExist(chat=support_chat))
        check_business_rule(ChatIsNotClosed(status=support_chat.status))
        check_business_rule(IsOperator(role=role))
        check_business_rule(WaitingAfterCreation(status=support_chat.status))

        support_chat.assign_operator(user_id)

        return await self.uow.chat_repository.persist(support_chat)

    @async_transaction()
    async def close_chat(self, chat_id: int, user: User) -> SupportChat | None:
        support_chat = await self._get_chat(chat_id)
        check_business_rule(SupportChatExist(chat=support_chat))
        check_business_rule(UserOwnChat(owner_id=support_chat.user_id, user_id=user.id))
        check_business_rule(ChatIsNotClosed(status=support_chat.status))

        support_chat.close_by_user()

        return await self.uow.chat_repository.persist(support_chat)
