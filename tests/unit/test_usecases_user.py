from __future__ import annotations

import pytest

from src.application.dto.user_dto import RegisterUser
from src.application.use_cases.user_use_case import UserUseCase
from src.domain.entities.user import User
from src.domain.repositories.user_repository import BaseUserRepository


class FakeUserRepository(BaseUserRepository):
    def __init__(self) -> None:
        self.storage: dict[int, User] = {}

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    async def save_user(self, user: User) -> User:
        self.storage[user.telegram_id] = user
        return user


@pytest.mark.asyncio
async def test_registers_new_user():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    dto = RegisterUser(telegram_id=1, username="ivan", full_name="Ivan Petrov")

    user = await use_case.register_user(dto)

    assert user.telegram_id == 1
    assert repository.storage[1] == user


@pytest.mark.asyncio
async def test_returns_existing_user_without_duplicating():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    dto = RegisterUser(telegram_id=1, username="ivan", full_name="Ivan Petrov")

    first = await use_case.register_user(dto)
    second = await use_case.register_user(dto)

    assert first == second
    assert len(repository.storage) == 1


@pytest.mark.asyncio
async def test_get_user():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    user_id = 1
    dto = RegisterUser(telegram_id=user_id, username="ivan", full_name="Ivan Petrov")

    user = await use_case.get_user(user_id)
    assert user is None

    await use_case.register_user(dto)
    user = await use_case.get_user(user_id)
    assert isinstance(user, User)
    assert user.telegram_id == user_id
