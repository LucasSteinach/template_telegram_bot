from datetime import datetime, timezone

from src.application.dto.user_dto import RegisterUser
from src.domain.entities.user import User
from src.infrastructure.database.repositories.user_repository import UserRepository


class UserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def get_or_create_user(self, dto: RegisterUser) -> User:
        exist = await self._user_repository.find_by_id(dto.id)
        if exist:
            return exist

        user = User(
            **dto.model_dump(mode="json"), created_at=datetime.now(tz=timezone.utc)
        )
        await self._user_repository.persist(user)
        return user

    async def get_user(self, user_id: int) -> User | None:
        exist = await self._user_repository.find_by_id(user_id)
        if not exist:
            return None

        return exist
