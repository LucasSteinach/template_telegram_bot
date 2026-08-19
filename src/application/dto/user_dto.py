from pydantic import BaseModel

from src.domain.entities.user import UserRole


class RegisterUser(BaseModel):
    id: int
    username: str | None
    full_name: str
    role: UserRole = UserRole.USER
