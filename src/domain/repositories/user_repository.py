from abc import ABC, abstractmethod

from src.domain.entities.user import User


class BaseUserRepository(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def save_user(self, user: User) -> None: ...
