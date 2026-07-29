import pytest
from sqlalchemy import text

from src.infrastructure.database.db import async_session_factory


@pytest.mark.asyncio
async def test_database_connection():
    async with async_session_factory() as test_session:
        result = await test_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
