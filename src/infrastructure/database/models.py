from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.domain.entities.user import UserRole


class ChatStatus(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    ACTIVE = "active"
    CLOSED = "closed"


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[UserRole] = mapped_column(String(64), nullable=False, default="user")
    full_name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
