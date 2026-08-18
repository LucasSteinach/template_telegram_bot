from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


class User(BaseModel):
    id: int
    username: str | None = None
    full_name: str
    created_at: datetime

    role: UserRole = UserRole.USER
