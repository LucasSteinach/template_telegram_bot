from application.services.auth import EmailLowercaseStr
from domain.entities.base_entity import Entity
from domain.entities.user import UserRole


class Operator(Entity):
    id: int
    email: EmailLowercaseStr
    password: str
    is_active: bool
    role: UserRole = UserRole.OPERATOR
