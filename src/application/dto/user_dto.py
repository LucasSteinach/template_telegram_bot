from dataclasses import dataclass

from src.domain.entities.user import UserRole


@dataclass
class RegisterUser:
    id: int
    username: str | None
    full_name: str
    role: UserRole = UserRole.USER
