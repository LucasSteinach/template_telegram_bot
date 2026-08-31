from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.usecases.base_use_case import AsyncBaseUnitOfWork
from domain.entities.operator import Operator
from domain.entities.user import User
from domain.rules.operator_rules import OperatorExist
from domain.rules.rules import check_business_rule
from domain.rules.user_rules import UserExist
from infrastructure.database.repositories.operator_repository import (
    OperatorRepository,
)
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.sqlalchemy.transaction import async_transaction


class OperatorUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self):
        await super().__aenter__()

        self.operator_repository: OperatorRepository = OperatorRepository(self.session)
        self.user_repository: UserRepository = UserRepository(self.session)


class OperatorUseCase:
    def __init__(self, uow: OperatorUnitOfWork) -> None:
        self.uow: OperatorUnitOfWork = uow

    async def _get_user(self, user_id: int) -> User | None:
        return await self.uow.user_repository.find_by_id(user_id)

    @async_transaction(read_only=True)
    async def get_user(self, user_id: int) -> User:
        user = await self._get_user(user_id)
        check_business_rule(UserExist(user=user))

        return user

    @async_transaction(read_only=True)
    async def get_operator(self, user_id: int) -> Operator:
        user = await self.get_user(user_id)
        operator = await self.uow.operator_repository.find_by_id(user.id)
        check_business_rule(OperatorExist(operator=operator))

        return operator

    @async_transaction(read_only=True)
    async def get_operator_by_email(self, email: str) -> Operator:
        operator = await self.uow.operator_repository.find_by_email(email)
        check_business_rule(OperatorExist(operator=operator))

        return operator
