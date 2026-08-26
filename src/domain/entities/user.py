from datetime import datetime
from enum import StrEnum

from src.domain.entities.base_entity import Entity


class UserRole(StrEnum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


class User(Entity):
    id: int
    username: str | None = None
    full_name: str
    created_at: datetime

    role: UserRole = UserRole.USER
