from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import BaseUserRepository
from src.infrastructure.database.models import UserModel


class UserRepository(BaseUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return User(
            telegram_id=row.telegram_id,
            username=row.username,
            full_name=row.full_name,
            created_at=row.created_at,
            role=row.role,
        )

    async def save_user(self, user: User) -> User:
        model = UserModel(
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
            role=user.role,
        )
        merged = await self._session.merge(model)

        await self._session.commit()
        await self._session.refresh(merged)

        return User(
            telegram_id=merged.telegram_id,
            username=merged.username,
            full_name=merged.full_name,
            created_at=merged.created_at,
            role=merged.role,
        )
