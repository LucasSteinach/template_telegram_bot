import datetime as d

import pytest

from src.domain.entities.user import User
from src.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


@pytest.mark.asyncio
async def test_db_user_repository(session):
    repository = SqlAlchemyUserRepository(session)

    no_user = await repository.get_by_telegram_id(-1)
    assert no_user is None

    user = User(
        telegram_id=123,
        username="test",
        full_name="Very Test User",
        created_at=d.datetime.now(),
    )

    await repository.save(user)

    user_exist = (await repository.get_by_telegram_id(user.telegram_id)) is not None
    assert user_exist
