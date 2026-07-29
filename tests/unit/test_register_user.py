from __future__ import annotations

import pytest

from src.application.dto.user_dto import RegisterUser
from src.application.use_cases.register_user import RegisterUserUseCase
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.storage: dict[int, User] = {}

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    async def save(self, user: User) -> None:
        self.storage[user.telegram_id] = user


@pytest.mark.asyncio
async def test_registers_new_user() -> None:
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(repository)
    dto = RegisterUser(telegram_id=1, username="ivan", full_name="Ivan Petrov")

    user = await use_case.execute(dto)

    assert user.telegram_id == 1
    assert repository.storage[1] == user


@pytest.mark.asyncio
async def test_returns_existing_user_without_duplicating() -> None:
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(repository)
    dto = RegisterUser(telegram_id=1, username="ivan", full_name="Ivan Petrov")

    first = await use_case.execute(dto)
    second = await use_case.execute(dto)

    assert first == second
    assert len(repository.storage) == 1
