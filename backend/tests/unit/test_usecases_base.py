from unittest.mock import AsyncMock

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.usecases.base_use_case import AsyncBaseUnitOfWork, SyncBaseUnitOfWork


def test_sync_base_uow(engine):
    session_factory = sessionmaker(
        create_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        ),
        class_=Session,
        expire_on_commit=False,
    )
    sync_uow = SyncBaseUnitOfWork(session_factory)

    assert sync_uow.session_factory == session_factory
    assert sync_uow.session is None

    with sync_uow:
        assert sync_uow.session is not None

    assert sync_uow.session.is_active


@pytest.mark.asyncio
async def test_async_base_uow(session_factory):
    async_uow = AsyncBaseUnitOfWork(session_factory)
    async_uow.exception = ValueError("Something went wrong in DB")
    session_factory.rollback = AsyncMock()

    assert async_uow.session_factory == session_factory
    assert async_uow.session is None

    with pytest.raises(ValueError, match="Something went wrong in DB"):
        async with async_uow:
            assert async_uow.session is not None

            raise async_uow.exception

        session_factory.rollback.assert_awaited_once()
