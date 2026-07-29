from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
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
        )

    async def save(self, user: User) -> None:
        model = UserModel(
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
        )
        self._session.add(model)
        await self._session.commit()
