from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.operator import Operator
from infrastructure.database.models import OperatorModel
from infrastructure.database.repositories.base_repository import AsyncBaseRepository


class OperatorRepository(AsyncBaseRepository[OperatorModel, Operator, int]):
    _instance = OperatorModel
    _entity = Operator

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def instance_to_entity(self, instance: OperatorModel) -> Operator:
        return Operator(
            id=instance.id,
            email=instance.email,
            password=instance.password,
            is_active=instance.is_active,
            role=instance.role,
        )

    def entity_to_instance(self, entity: Operator) -> OperatorModel:
        return OperatorModel(
            id=entity.id,
            email=entity.email,
            password=entity.password,
            is_active=entity.is_active,
            role=entity.role,
        )

    async def find_by_email(self, email: str) -> Operator | None:
        stmt = select(self._instance)
        stmt = stmt.where(self._instance.email == email)
        item = await self._session.execute(stmt)
        instance: OperatorModel | None = item.scalars().one_or_none()

        if instance:
            return self.instance_to_entity(instance)
