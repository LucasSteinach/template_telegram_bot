from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.infrastructure.database.models import SupportChatModel
from src.infrastructure.database.repositories.base_repository import AsyncBaseRepository


class SupportChatRepository(AsyncBaseRepository[SupportChatModel, SupportChat, int]):
    _instance = SupportChatModel
    _entity = SupportChat

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def instance_to_entity(self, instance: SupportChatModel) -> SupportChat:
        return SupportChat(
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

    def entity_to_instance(self, entity: SupportChat) -> SupportChatModel:
        return SupportChatModel(
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

    async def get_open_chats(self) -> list[SupportChat]:
        result = await self.find_all(
            where=[
                SupportChatModel.status != ChatStatus.CLOSED,
            ]
        )
        return result.items

    async def get_assigned_chats(self, operator_id: int) -> list[SupportChat]:
        result = await self.find_all(
            where=[
                SupportChatModel.operator_id == operator_id,
            ]
        )
        return result.items

    async def get_active_chats(self) -> list[SupportChat]:
        result = await self.find_all(
            where=[
                SupportChatModel.status == ChatStatus.ACTIVE,
            ]
        )
        return result.items

    async def get_all_by_user_id(self, user_id: int) -> list[SupportChat]:
        result = await self.find_all(
            where=[
                SupportChatModel.user_id == user_id,
            ]
        )
        return result.items

    async def get_all_closed_chats(self) -> list[SupportChat]:
        result = await self.find_all(
            where=[
                SupportChatModel.status == ChatStatus.CLOSED,
            ]
        )
        return result.items
