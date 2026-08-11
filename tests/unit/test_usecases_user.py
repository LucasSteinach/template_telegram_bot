from __future__ import annotations

import pytest

from src.application.dto.user_dto import RegisterUser
from src.application.use_cases.user_use_case import UserUseCase
from src.domain.entities.user import User


class FakeUserRepository:
    def __init__(self) -> None:
        self.storage: dict[int, User] = {}

    async def find_by_id(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    async def persist(self, user: User) -> User:
        self.storage[user.id] = user
        return user


@pytest.mark.asyncio
async def test_registers_new_user():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    user = await use_case.get_or_create_user(dto)

    assert user.id == 1
    assert repository.storage[1] == user


@pytest.mark.asyncio
async def test_returns_existing_user_without_duplicating():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    first = await use_case.get_or_create_user(dto)
    second = await use_case.get_or_create_user(dto)

    assert first == second
    assert len(repository.storage) == 1


@pytest.mark.asyncio
async def test_get_user():
    repository = FakeUserRepository()
    use_case = UserUseCase(repository)
    user_id = 1
    dto = RegisterUser(id=user_id, username="ivan", full_name="Ivan Petrov")

    user = await use_case.get_user(user_id)
    assert user is None

    await use_case.get_or_create_user(dto)
    user = await use_case.get_user(user_id)
    assert isinstance(user, User)
    assert user.id == user_id
