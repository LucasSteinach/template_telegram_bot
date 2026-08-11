from src.domain.entities.support_message import SupportMessage
from src.infrastructure.database.repositories.support_message_repository import (
    SupportMessageRepository,
)


class SupportMessageUseCase:
    def __init__(self, support_message_repository: SupportMessageRepository) -> None:
        self._support_message_repository = support_message_repository

    async def get_message(self, message_id: int) -> SupportMessage | None:
        return await self._support_message_repository.find_by_id(message_id)

    async def save_message(
        self,
        chat_id: int,
        author_id: int,
        author_role: str,
        text: str,
        id_: int | None = None,
    ) -> SupportMessage:
        return await self._support_message_repository.persist(
            SupportMessage(
                id=id_,
                chat_id=chat_id,
                author_id=author_id,
                author_role=author_role,
                text=text,
            )
        )
