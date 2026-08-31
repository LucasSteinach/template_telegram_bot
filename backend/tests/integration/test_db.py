import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(container):
    async with container.session_factory() as test_session:
        result = await test_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
