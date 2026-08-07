from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


@dataclass
class User:
    telegram_id: int
    username: str | None
    full_name: str
    created_at: datetime

    role: UserRole = UserRole.USER
