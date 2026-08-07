from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.support_chat import ChatStatus
from src.domain.entities.support_chat import SupportChat as Entity
from src.domain.repositories.support_chat_repository import BaseSupportChatRepository
from src.infrastructure.database.models import SupportChatModel as Instance


class SupportChatRepository(BaseSupportChatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def entity_to_instance(entity: Entity) -> Instance:
        return Instance(
            id=entity.id,
            topic=entity.topic,
            user_id=entity.user_id,
            operator_id=entity.operator_id,
            status=entity.status,
            created_at=entity.created_at,
            last_activity_at=entity.last_activity_at,
            closed_at=entity.closed_at,
            closed_by=entity.closed_by,
        )

    @staticmethod
    def instance_to_entity(instance: Instance) -> Entity:
        return Entity(
            id=instance.id,
            topic=instance.topic,
            user_id=instance.user_id,
            operator_id=instance.operator_id,
            status=instance.status,
            created_at=instance.created_at,
            last_activity_at=instance.last_activity_at,
            closed_at=instance.closed_at,
            closed_by=instance.closed_by,
        )

    async def get_chat(self, chat_id: int) -> Entity | None:
        result = await self._session.execute(
            select(Instance).where(Instance.id == chat_id)
        )
        instance = result.scalar_one_or_none()
        if instance is None:
            return None
        return self.instance_to_entity(instance)

    async def get_active_chats(self) -> list[Entity]:
        result = await self._session.execute(
            select(Instance)
            .where(
                Instance.status != ChatStatus.CLOSED,
            )
            .order_by(~Instance.last_activity_at)
        )
        instances = result.scalars().all()

        if instances is None:
            return []
        return [self.instance_to_entity(instance) for instance in instances]

    async def get_chats_by_user(self, user_id: int) -> list[Entity]:
        result = await self._session.execute(
            select(Instance)
            .where(
                Instance.user_id == user_id,
            )
            .order_by(Instance.last_activity_at)
        )
        instances = result.scalars().all()

        if instances is None:
            return []
        return [self.instance_to_entity(instance) for instance in instances]

    async def get_closed_chats(self) -> list[Entity]:
        result = await self._session.execute(
            select(Instance)
            .where(
                Instance.status == ChatStatus.CLOSED,
            )
            .order_by(Instance.last_activity_at)
        )
        instances = result.scalars().all()

        if instances is None:
            return []
        return [self.instance_to_entity(instance) for instance in instances]

    async def persist(self, entity: Entity) -> Entity:
        instance = self.entity_to_instance(entity)

        merged = await self._session.merge(instance)

        await self._session.commit()
        await self._session.refresh(merged)

        return self.instance_to_entity(merged)
