import pytest

from application.usecases.operator_use_case import OperatorUnitOfWork, OperatorUseCase
from domain.entities.operator import Operator
from domain.entities.user import User
from domain.exceptions import BusinessLogicException
from infrastructure.database.repositories.operator_repository import OperatorRepository
from infrastructure.database.repositories.user_repository import UserRepository


class FakeOperatorRepository:
    def __init__(self) -> None:
        self.storage: dict[int, Operator] = {}

    async def find_by_id(self, id_: int) -> User | None:
        return self.storage.get(id_)

    async def find_by_email(self, email: str) -> Operator | None:
        return next(
            (
                operator
                for _, operator in self.storage.items()
                if operator.email == email
            ),
            None,
        )

    async def persist(self, operator: Operator) -> Operator:
        self.storage.update({operator.id: operator})
        return operator


class FakeUserRepository:
    def __init__(self) -> None:
        self.storage: dict[int, User] = {}

    async def find_by_id(self, telegram_id: int) -> User | None:
        return self.storage.get(telegram_id)

    async def persist(self, user: User) -> User:
        self.storage[user.id] = user
        return user


class FakeUnitOfWork(OperatorUnitOfWork):
    def __init__(self, session_factory=None) -> None:
        super().__init__(session_factory)

        self.operator_repository: FakeOperatorRepository = FakeOperatorRepository()
        self.user_repository: FakeUserRepository = FakeUserRepository()

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()


@pytest.mark.asyncio
async def test_operator_uow(session_factory):
    uow = OperatorUnitOfWork(session_factory=session_factory)
    assert uow.session_factory == session_factory

    async with uow:
        assert isinstance(uow.operator_repository, OperatorRepository)
        assert isinstance(uow.user_repository, UserRepository)


@pytest.mark.asyncio
async def test_get_user(user_entity, session_factory):
    use_case = OperatorUseCase(FakeUnitOfWork(session_factory=session_factory))
    entity = user_entity()

    with pytest.raises(BusinessLogicException, match="user not exist"):
        await use_case.get_user(entity.id)

    await use_case.uow.user_repository.persist(entity)
    user = await use_case.get_user(entity.id)

    assert isinstance(user, User)
    assert user.id == entity.id


@pytest.mark.asyncio
async def test_get_operator(user_entity, operator_entity, session_factory):
    use_case = OperatorUseCase(FakeUnitOfWork(session_factory=session_factory))
    user = user_entity(id=1)
    operator = operator_entity(id=1)

    with pytest.raises(BusinessLogicException, match="user not exist"):
        await use_case.get_user(user.id)

    await use_case.uow.user_repository.persist(user)

    with pytest.raises(BusinessLogicException, match="operator not exist"):
        await use_case.get_operator(user.id)

    await use_case.uow.operator_repository.persist(operator)

    operator = await use_case.get_operator(user.id)

    assert isinstance(operator, Operator)
    assert operator.id == user.id


@pytest.mark.asyncio
async def test_get_operator_by_email(operator_entity, session_factory):
    use_case = OperatorUseCase(FakeUnitOfWork(session_factory=session_factory))
    entity = operator_entity(id=1)

    with pytest.raises(BusinessLogicException, match="operator not exist"):
        await use_case.get_operator_by_email(entity.email)

    await use_case.uow.operator_repository.persist(entity)

    operator = await use_case.get_operator_by_email(entity.email)

    assert isinstance(operator, Operator)
    assert operator.id == entity.id
