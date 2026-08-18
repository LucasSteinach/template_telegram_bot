import logging
from dataclasses import field
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel

from src.domain.entities.user import UserRole

logger = logging.getLogger(__name__)


class ChatStatus(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    ACTIVE = "active"
    CLOSED = "closed"


class SupportChat(BaseModel):
    user_id: int

    id: int | None = None
    topic: str | None = None

    operator_id: int | None = None
    closed_at: datetime | None = None
    closed_by: str | None = None
    last_activity_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    status: ChatStatus = ChatStatus.CREATED

    def assign_operator(self, operator_id: int):
        self.operator_id = operator_id
        self.active()

    def waiting(self):
        self.status = ChatStatus.WAITING

    def active(self):
        self.status = ChatStatus.ACTIVE

    def close(self, user_id: int, role: str) -> None:
        if user_id not in [self.user_id, self.operator_id] and role != UserRole.ADMIN:
            logger.warning(f"{role}: {user_id} had attempt to close chat: {self.id}")
            return
        if user_id == self.user_id:
            self._close_by_user()
        elif self.operator_id == user_id or role == UserRole.ADMIN:
            self._close_by_operator(user_id, role)

        self.status = ChatStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)

    def _close_by_user(self):
        self.closed_by = "user"

    def _close_by_operator(self, user_id: int, role: str):
        self.closed_by = f"{role}:{user_id}"
