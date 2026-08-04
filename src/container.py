from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.db import async_session_factory
from src.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from src.infrastructure.redis.storage import RedisStorage


class Container:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.settings = settings
        self.redis_storage: RedisStorage = RedisStorage(
            Redis.from_url(settings.redis_url)
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_session_factory

    def register_user_use_case(self, session: AsyncSession) -> RegisterUserUseCase:
        repository = SqlAlchemyUserRepository(session)
        return RegisterUserUseCase(repository)
