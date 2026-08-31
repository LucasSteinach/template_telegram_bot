from src.application.services.auth import EmailLowercaseStr
from src.domain.entities.base_entity import Entity
from src.domain.entities.user import UserRole


class Operator(Entity):
    id: int
    email: EmailLowercaseStr
    password: str
    is_active: bool
    role: UserRole = UserRole.OPERATOR
