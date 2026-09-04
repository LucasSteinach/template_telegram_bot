from unittest.mock import AsyncMock, MagicMock

import pytest

from infrastructure.database.sqlalchemy.transaction import (
    async_transaction,
    sync_transaction,
)


@pytest.mark.asyncio
async def test_async_transaction_read_only():
    mock_session = MagicMock()
    mock_session.in_transaction.return_value = False
    mock_session.bind.dialect.name = "postgresql"

    mock_session.execute = AsyncMock()

    mock_uow = AsyncMock()
    mock_uow.session = mock_session

    class FakeUseCase:
        def __init__(self):
            self.uow = mock_uow

        @async_transaction(read_only=True)
        async def double(self, x):
            return x * 2

    use_case = FakeUseCase()

    result = await use_case.double(5)

    assert result == 10

    mock_session.execute.assert_awaited_once()
    assert "SET TRANSACTION READ ONLY" in mock_session.execute.call_args[0][0].text


@pytest.mark.asyncio
async def test_async_transaction_in_transaction():
    mock_session = MagicMock()
    mock_session.in_transaction.return_value = True

    mock_uow = AsyncMock()
    mock_uow.session = mock_session

    class FakeUseCase:
        def __init__(self):
            self.uow = mock_uow

        @async_transaction(read_only=True)
        async def double(self, x):
            return x * 2

    use_case = FakeUseCase()

    result = await use_case.double(5)

    assert result == 10


def test_sync_transaction_read_only():
    mock_session = MagicMock()
    mock_session.begin.return_value.__enter__ = MagicMock()
    mock_session.begin.return_value.__exit__ = MagicMock()
    mock_session.bind.dialect.name = "postgresql"

    mock_uow = MagicMock()
    mock_uow.__enter__ = MagicMock()
    mock_uow.__exit__ = MagicMock()
    mock_uow.session = mock_session

    class FakeUseCase:
        def __init__(self):
            self.uow = mock_uow

        @sync_transaction(read_only=True)
        def increment(self, x):
            return x + 1

    use_case = FakeUseCase()

    result = use_case.increment(5)

    assert result == 6
    mock_uow.__enter__.assert_called_once()
    mock_session.begin.return_value.__enter__.assert_called_once()
    mock_session.execute.assert_called_once()
    assert "SET TRANSACTION READ ONLY" in mock_session.execute.call_args[0][0].text
