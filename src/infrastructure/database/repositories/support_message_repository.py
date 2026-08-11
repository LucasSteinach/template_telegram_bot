from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.support_message import SupportMessage
from src.infrastructure.database.models import SupportMessageModel
from src.infrastructure.database.repositories.base_repository import AsyncBaseRepository


class SupportMessageRepository(
    AsyncBaseRepository[SupportMessageModel, SupportMessage, int]
):
    _instance = SupportMessageModel
    _entity = SupportMessage

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def entity_to_instance(self, entity: SupportMessage) -> SupportMessageModel:
        return SupportMessageModel(
            id=entity.id,
            chat_id=entity.chat_id,
            author_id=entity.author_id,
            author_role=entity.author_role,
            text=entity.text,
            created_at=entity.created_at,
        )

    def instance_to_entity(self, instance: SupportMessageModel) -> SupportMessage:
        return SupportMessage(
            id=instance.id,
            chat_id=instance.chat_id,
            author_id=instance.author_id,
            author_role=instance.author_role,
            text=instance.text,
            created_at=instance.created_at,
        )

    async def get_all_by_chat_id(self, chat_id: int) -> list[SupportMessage]:
        result = await self.find_all(
            where=[
                SupportMessageModel.chat_id == chat_id,
            ]
        )

        return result.items
