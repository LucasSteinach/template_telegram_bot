import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from application.services.auth import hash_password
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


# ======================================
# Create test instances
# ======================================


@pytest_asyncio.fixture
async def create_test_operator(app, operator_instance, clean_db):
    uow = app.state.container.operator_uow()

    new_operator = operator_instance(
        email="test@test.com",
        password=hash_password("12345678"),
    )

    async with uow, uow.session.begin():
        uow.session.add(new_operator)

    yield new_operator


@pytest_asyncio.fixture
async def create_test_user(app, user_instance, clean_db):
    uow = app.state.container.user_uow()

    new_user = user_instance(
        username="test_user",
        full_name="Test User",
        role="operator",
    )

    async with uow, uow.session.begin():
        uow.session.add(new_user)

    yield new_user


@pytest_asyncio.fixture
async def create_support_chat(app, support_chat_instance, clean_db):
    uow = app.state.container.support_chat_uow()

    new_chat = support_chat_instance(
        operator_id=12341234,
        status="waiting",
    )

    async with uow, uow.session.begin():
        uow.session.add(new_chat)

    yield new_chat


@pytest_asyncio.fixture
async def create_support_message(app, support_message_instance, clean_db):
    uow = app.state.container.support_message_uow()

    new_message = support_message_instance()

    async with uow, uow.session.begin():
        uow.session.add(new_message)

    yield new_message
