import pytest

from application.usecases.user_use_case import (
    RegisterUser,
    UserUnitOfWork,
    UserUseCase,
)
from domain.entities.user import User
from domain.exceptions import BusinessLogicException


class FakeUserRepository:
    def __init__(self) -> None:
        self.storage: dict[int, User] = {}

    async def find_by_id(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    async def persist(self, user: User) -> User:
        self.storage[user.id] = user
        return user


class FakeUnitOfWork(UserUnitOfWork):
    def __init__(self, session_factory=None) -> None:
        super().__init__(session_factory)

        self.user_repository: FakeUserRepository = FakeUserRepository()


@pytest.mark.asyncio
async def test_registers_new_user():
    use_case = UserUseCase(FakeUnitOfWork())
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    user = await use_case.get_or_create_user.__wrapped__(use_case, dto)

    assert user.id == 1
    assert use_case.uow.user_repository.storage[1] == user


@pytest.mark.asyncio
async def test_returns_existing_user_without_duplicating():
    use_case = UserUseCase(FakeUnitOfWork())
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    first = await use_case.get_or_create_user.__wrapped__(use_case, dto)
    second = await use_case.get_or_create_user.__wrapped__(use_case, dto)

    assert first.id == second.id
    assert len(use_case.uow.user_repository.storage) == 1


@pytest.mark.asyncio
async def test_get_user():
    use_case = UserUseCase(FakeUnitOfWork())
    user_id = 1
    dto = RegisterUser(id=user_id, username="ivan", full_name="Ivan Petrov")

    with pytest.raises(BusinessLogicException, match="user not exist"):
        await use_case.get_user.__wrapped__(use_case, user_id)

    await use_case.get_or_create_user.__wrapped__(use_case, dto)
    user = await use_case.get_user.__wrapped__(use_case, user_id)
    assert isinstance(user, User)
    assert user.id == user_id
