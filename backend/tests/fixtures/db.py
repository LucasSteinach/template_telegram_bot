import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from infrastructure.database.models import BaseModel


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine

    await engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def session(engine, session_factory):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_db(engine):
    yield

    async with engine.begin() as conn:
        for table in reversed(BaseModel.metadata.sorted_tables):
            await conn.execute(table.delete())
