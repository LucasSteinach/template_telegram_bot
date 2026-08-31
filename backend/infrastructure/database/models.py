from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain.entities.support_chat import ChatStatus
from domain.entities.user import UserRole


class BaseModel(DeclarativeBase):
    pass


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[UserRole] = mapped_column(String(64), nullable=False, default="user")
    full_name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class OperatorModel(BaseModel):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="operator", nullable=False)


class SupportChatModel(BaseModel):
    __tablename__ = "support_chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    topic: Mapped[str] = mapped_column(String(64), nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    status: Mapped[ChatStatus] = mapped_column(
        Enum(ChatStatus), nullable=False, default=ChatStatus.CREATED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by: Mapped[str] = mapped_column(String(64), nullable=True)
    messages: Mapped[list["SupportMessageModel"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class SupportMessageModel(BaseModel):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("support_chats.id", ondelete="CASCADE"), nullable=False
    )
    author_role: Mapped[str] = mapped_column(String(64), nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    chat: Mapped["SupportChatModel"] = relationship(back_populates="messages")
