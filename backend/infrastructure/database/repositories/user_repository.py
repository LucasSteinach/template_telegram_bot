from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from infrastructure.database.models import UserModel
from infrastructure.database.repositories.base_repository import AsyncBaseRepository


class UserRepository(AsyncBaseRepository[UserModel, User, int]):
    _instance = UserModel
    _entity = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def instance_to_entity(self, instance: UserModel) -> User:
        return User(
            id=instance.id,
            username=instance.username,
            full_name=instance.full_name,
            created_at=instance.created_at,
            role=instance.role,
        )

    def entity_to_instance(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            full_name=entity.full_name,
            created_at=entity.created_at,
            role=entity.role,
        )
