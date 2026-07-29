from datetime import datetime, timezone

from src.application.dto.user_dto import RegisterUser
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, dto: RegisterUser) -> User:
        exist = await self._user_repository.get_by_telegram_id(dto.telegram_id)
        if exist:
            return exist

        user = User(
            telegram_id=dto.telegram_id,
            username=dto.username,
            full_name=dto.full_name,
            created_at=datetime.now(timezone.utc),
        )
        await self._user_repository.save(user)
        return user
