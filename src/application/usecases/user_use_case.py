from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.usecases.base_use_case import AsyncBaseUnitOfWork
from src.domain.entities.user import User, UserRole
from src.domain.rules.rules import check_business_rule
from src.domain.rules.user_rules import UserExist
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.sqlalchemy.transaction import async_transaction


class GetUser(BaseModel):
    id: int


class RegisterUser(BaseModel):
    id: int
    username: str | None
    full_name: str
    role: UserRole = UserRole.USER


class UserReadModel(BaseModel):
    id: int
    username: str = ""
    full_name: str


def user_read_model(u: User):
    return UserReadModel(
        id=u.id,
        username=u.username,
        full_name=u.full_name,
    )


class UserUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self):
        await super().__aenter__()

        self.user_repository: UserRepository = UserRepository(self.session)


class UserUseCase:
    def __init__(self, uow: UserUnitOfWork) -> None:
        self.uow: UserUnitOfWork = uow

    async def _get_user(self, user_id: int) -> User | None:
        return await self.uow.user_repository.find_by_id(user_id)

    @async_transaction(read_only=True)
    async def get_user(self, user_id: int) -> User:
        user = await self._get_user(user_id)
        check_business_rule(UserExist(user=user))

        return user

    @async_transaction()
    async def get_or_create_user(self, dto: RegisterUser) -> User:
        exist = await self._get_user(dto.id)
        if exist:
            return exist

        user = User(
            **dto.model_dump(mode="json"), created_at=datetime.now(tz=timezone.utc)
        )

        await self.uow.user_repository.persist(user)
        return user
