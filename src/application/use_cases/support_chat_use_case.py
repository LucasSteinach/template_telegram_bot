import logging

from src.domain.entities.support_chat import SupportChat
from src.domain.entities.user import User
from src.infrastructure.database.repositories.support_chat_repository import (
    SupportChatRepository,
)

logger = logging.getLogger(__name__)


class SupportChatUseCase:
    def __init__(self, support_chat_repository: SupportChatRepository) -> None:
        self._support_chat_repository = support_chat_repository

    async def get_chat(self, chat_id: int) -> SupportChat | None:
        return await self._support_chat_repository.find_by_id(chat_id)

    async def create_chat(self, user_id: int, id_: int | None = None) -> SupportChat:
        return await self._support_chat_repository.persist(
            SupportChat(
                id=id_,
                user_id=user_id,
            )
        )

    async def close_chat(self, chat_id: int, user: User) -> SupportChat | None:
        chat = await self._support_chat_repository.find_by_id(chat_id)
        if not chat:
            return
        chat.close(user.id, user.role)
        return await self.save_chat(chat)

    async def save_chat(self, chat: SupportChat) -> SupportChat:
        await self._support_chat_repository.persist(chat)
        return chat
