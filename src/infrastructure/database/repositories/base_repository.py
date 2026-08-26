from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy import ColumnElement, Sequence, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import BaseModel

EntityT = TypeVar("EntityT")
ModelT = TypeVar("ModelT", bound=BaseModel)
IDT = TypeVar("IDT")


@dataclass
class FindAllResult(Generic[EntityT]):
    total: int | None
    items: list[EntityT]


class AsyncBaseRepository(ABC, Generic[ModelT, EntityT, IDT]):
    _instance: type[ModelT]
    _entity: type[EntityT]
    _id_field_name: str = "id"

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    @property
    def id_field(self):
        return getattr(self._instance, self._id_field_name)

    @abstractmethod
    def instance_to_entity(self, instance: ModelT) -> EntityT: ...

    @abstractmethod
    def entity_to_instance(self, entity: EntityT) -> ModelT: ...

    async def find_by_id(self, id_: IDT) -> EntityT | None:
        stmt = select(self._instance)
        stmt = stmt.where(self.id_field == id_)
        item = await self._session.execute(stmt)
        instance: ModelT | None = item.scalars().one_or_none()

        if instance:
            return self.instance_to_entity(instance)

    async def find_by_ids(self, ids: list[IDT]) -> list[EntityT]:
        if not ids:
            return []

        stmt = select(self._instance)
        stmt = stmt.where(self.id_field.in_(ids))
        items = await self._session.execute(stmt)
        instances = items.scalars().all()
        return [self.instance_to_entity(instance) for instance in instances]

    async def find_all(
        self,
        *,
        where: Sequence[ColumnElement[bool]] | None = None,
        order_by: Sequence[Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_total: bool = False,
    ) -> FindAllResult[EntityT]:
        stmt = select(self._instance)
        total: int | None = None

        if where:
            stmt = stmt.where(*where)

        if include_total:
            count = select(func.count()).select_from(stmt.subquery())
            total = await self._session.scalar(count)

        if order_by:
            stmt = stmt.order_by(*order_by)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self._session.execute(stmt)
        instances = result.scalars().all()
        items = [self.instance_to_entity(instance) for instance in instances]

        return FindAllResult(total=total, items=items)

    async def persist(self, entity: EntityT) -> EntityT:
        instance = self.entity_to_instance(entity)
        merged = await self._session.merge(instance)

        await self._session.flush()

        return self.instance_to_entity(merged)

    async def delete(self, id_: IDT) -> None:
        instance = await self._session.get(self._instance, id_)
        if instance is not None:
            await self._session.delete(instance)
