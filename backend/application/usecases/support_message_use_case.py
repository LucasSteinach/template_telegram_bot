from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.usecases.base_use_case import AsyncBaseUnitOfWork
from domain.entities.support_message import SupportMessage
from domain.rules.rules import check_business_rule
from domain.rules.support_message_rules import ChatHasMessages, SupportMessageExist
from infrastructure.database.repositories.support_message_repository import (
    SupportMessageRepository,
)
from infrastructure.database.sqlalchemy.transaction import async_transaction


class SendSupportMessage(BaseModel):
    text: str


class SupportMessageReadModel(BaseModel):
    id: int
    chat_id: int
    author_id: int
    author_role: str
    text: str
    created_at: datetime


class HistoryMessage(BaseModel):
    id: int
    author: str
    created_at: datetime
    text: str


class ChatHistory(BaseModel):
    chat_id: int
    messages: list[HistoryMessage]


def support_message_read_model(sm: SupportMessage):
    return SupportMessageReadModel(
        id=sm.id,
        chat_id=sm.chat_id,
        author_id=sm.author_id,
        author_role=sm.author_role,
        text=sm.text,
        created_at=sm.created_at,
    )


def chat_history(messages: list[SupportMessage]):
    return ChatHistory(
        chat_id=messages[0].chat_id,
        messages=[
            HistoryMessage(
                id=m.id,
                author=f"{m.author_role.upper()}_{m.author_id}",
                created_at=m.created_at,
                text=m.text,
            )
            for m in messages
        ],
    )


class SupportMessageUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self):
        await super().__aenter__()

        self.message_repository: SupportMessageRepository = SupportMessageRepository(
            self.session
        )


class SupportMessageUseCase:
    def __init__(self, uow: SupportMessageUnitOfWork) -> None:
        self.uow: SupportMessageUnitOfWork = uow

    async def _get_message(self, message_id: int) -> SupportMessage | None:
        return await self.uow.message_repository.find_by_id(message_id)

    @async_transaction(read_only=True)
    async def get_message(self, message_id: int) -> SupportMessage:
        support_message = await self._get_message(message_id)
        check_business_rule(SupportMessageExist(message=support_message))

        return support_message

    @async_transaction(read_only=True)
    async def get_chat_history(self, chat_id: int) -> list[SupportMessage]:
        messages = await self.uow.message_repository.get_all_by_chat_id(chat_id)
        check_business_rule(ChatHasMessages(messages=messages))

        return messages

    @async_transaction()
    async def save_message(
        self,
        chat_id: int,
        author_id: int,
        author_role: str,
        text: str,
        id_: int | None = None,
    ) -> SupportMessage:
        return await self.uow.message_repository.persist(
            SupportMessage(
                id=id_,
                chat_id=chat_id,
                author_id=author_id,
                author_role=author_role,
                text=text,
            )
        )
