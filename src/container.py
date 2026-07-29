from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


class Container:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    def register_user_use_case(self, session: AsyncSession) -> RegisterUserUseCase:
        repository = SqlAlchemyUserRepository(session)
        return RegisterUserUseCase(repository)
