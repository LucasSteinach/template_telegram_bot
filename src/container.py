from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.use_cases.support_chat_use_case import SupportChatUseCase
from src.application.use_cases.support_message_use_case import SupportMessageUseCase
from src.application.use_cases.user_use_case import UserUseCase
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.db import async_session_factory
from src.infrastructure.database.repositories.support_chat_repository import (
    SupportChatRepository,
)
from src.infrastructure.database.repositories.support_message_repository import (
    SupportMessageRepository,
)
from src.infrastructure.database.repositories.user_repository import (
    UserRepository,
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

    def user_uc(self, session: AsyncSession) -> UserUseCase:
        return UserUseCase(UserRepository(session))

    def support_chat_uc(self, session: AsyncSession) -> SupportChatUseCase:
        return SupportChatUseCase(SupportChatRepository(session))

    def support_message_uc(self, session: AsyncSession) -> SupportMessageUseCase:
        return SupportMessageUseCase(SupportMessageRepository(session))
