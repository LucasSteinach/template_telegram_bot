from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.support_message import SupportMessage as Entity
from src.domain.repositories.support_message_repository import (
    BaseSupportMessageRepository,
)
from src.infrastructure.database.models import SupportMessageModel as Instance


class SupportMessageRepository(BaseSupportMessageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def entity_to_instance(entity: Entity) -> Instance:
        return Instance(
            id=entity.id,
            chat_id=entity.chat_id,
            author_id=entity.author_id,
            author_role=entity.author_role,
            text=entity.text,
            created_at=entity.created_at,
        )

    @staticmethod
    def instance_to_entity(instance: Instance) -> Entity:
        return Entity(
            id=instance.id,
            chat_id=instance.chat_id,
            author_id=instance.author_id,
            author_role=instance.author_role,
            text=instance.text,
            created_at=instance.created_at,
        )

    async def get_message(self, message_id: int) -> Entity | None:
        result = await self._session.execute(
            select(Instance).where(Instance.id == message_id)
        )
        instance = result.scalar_one_or_none()

        if instance is None:
            return None
        return self.instance_to_entity(instance)

    async def get_messages_by_chat(self, chat_id: int) -> list[Entity]:
        result = await self._session.execute(
            select(Instance).where(Instance.chat_id == chat_id)
        )
        instances = result.scalars().all()

        return [self.instance_to_entity(instance) for instance in instances]

    async def persist(self, entity: Entity) -> Entity:
        instance = self.entity_to_instance(entity)

        merged = await self._session.merge(instance)

        await self._session.commit()
        await self._session.refresh(merged)

        return self.instance_to_entity(merged)
