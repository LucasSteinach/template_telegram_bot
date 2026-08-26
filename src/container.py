from urllib.parse import quote_plus

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.services.auth import AuthService
from src.application.usecases.operator_use_case import (
    OperatorUnitOfWork,
    OperatorUseCase,
)
from src.application.usecases.support_chat_use_case import (
    SupportChatUnitOfWork,
    SupportChatUseCase,
)
from src.application.usecases.support_message_use_case import (
    SupportMessageUnitOfWork,
    SupportMessageUseCase,
)
from src.application.usecases.user_use_case import UserUnitOfWork, UserUseCase
from src.config import Settings
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
        self.engine: AsyncEngine = create_async_engine(
            f"postgresql+asyncpg://"
            f"{settings.db_user}:"
            f"{quote_plus(settings.db_password)}@"
            f"{settings.db_host}:"
            f"{settings.db_port}/"
            f"{settings.db_name}",
            echo=False,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def auth_service(self) -> AuthService:
        return AuthService(
            jwt_secret=self.settings.jwt_secret,
            access_exp_sec=self.settings.access_exp_sec,
            refresh_exp_sec=self.settings.refresh_exp_sec,
            redis=self.redis_storage,
        )

    def user_uow(self) -> UserUnitOfWork:
        return UserUnitOfWork(self.session_factory)

    def user_uc(self) -> UserUseCase:
        return UserUseCase(self.user_uow())

    def operator_uow(self) -> OperatorUnitOfWork:
        return OperatorUnitOfWork(self.session_factory)

    def operator_uc(self) -> OperatorUseCase:
        return OperatorUseCase(self.operator_uow())

    def support_chat_uow(self) -> SupportChatUnitOfWork:
        return SupportChatUnitOfWork(self.session_factory)

    def support_chat_uc(self) -> SupportChatUseCase:
        return SupportChatUseCase(self.support_chat_uow())

    def support_message_uow(self) -> SupportMessageUnitOfWork:
        return SupportMessageUnitOfWork(self.session_factory)

    def support_message_uc(self) -> SupportMessageUseCase:
        return SupportMessageUseCase(self.support_message_uow())
