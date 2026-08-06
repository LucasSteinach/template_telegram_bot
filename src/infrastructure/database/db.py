from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.config.settings import settings

engine = create_async_engine(
    f"postgresql+asyncpg://"
    f"{settings.db_user}:"
    f"{quote_plus(settings.db_password)}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}",
    echo=False,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
