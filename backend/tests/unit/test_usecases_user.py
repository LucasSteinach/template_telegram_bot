import pytest

from application.usecases.user_use_case import (
    RegisterUser,
    UserReadModel,
    UserUnitOfWork,
    UserUseCase,
    user_read_model,
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

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()


def test_user_read_model(user_entity):
    user = user_entity()

    read_model = user_read_model(user)

    assert isinstance(read_model, UserReadModel)
    assert read_model.id == user.id
    assert read_model.model_dump().get("role", None) is None


@pytest.mark.asyncio
async def test_registers_new_user(session_factory):
    use_case = UserUseCase(FakeUnitOfWork(session_factory))
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    user = await use_case.get_or_create_user(dto)

    assert user.id == 1
    assert use_case.uow.user_repository.storage[1] == user


@pytest.mark.asyncio
async def test_returns_existing_user_without_duplicating(session_factory):
    use_case = UserUseCase(FakeUnitOfWork(session_factory))
    dto = RegisterUser(id=1, username="ivan", full_name="Ivan Petrov")

    first = await use_case.get_or_create_user(dto)
    second = await use_case.get_or_create_user(dto)

    assert first.id == second.id
    assert len(use_case.uow.user_repository.storage) == 1


@pytest.mark.asyncio
async def test_get_user(session_factory):
    use_case = UserUseCase(FakeUnitOfWork(session_factory))
    user_id = 1
    dto = RegisterUser(id=user_id, username="ivan", full_name="Ivan Petrov")

    with pytest.raises(BusinessLogicException, match="user not exist"):
        await use_case.get_user(user_id)

    await use_case.get_or_create_user(dto)
    user = await use_case.get_user(user_id)
    assert isinstance(user, User)
    assert user.id == user_id
