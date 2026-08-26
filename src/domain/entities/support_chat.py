import logging
from dataclasses import field
from datetime import datetime, timezone
from enum import Enum

from src.domain.entities.base_entity import Entity

logger = logging.getLogger(__name__)


class ChatStatus(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    ACTIVE = "active"
    CLOSED = "closed"


class SupportChat(Entity):
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
        self.status = ChatStatus.ACTIVE
        self.last_activity_at = datetime.now(timezone.utc)

    def set_waiting(self):
        self.status = ChatStatus.WAITING
        self.last_activity_at = datetime.now(timezone.utc)

    def _close(self) -> None:
        self.status = ChatStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)

    def close_by_user(self):
        self.closed_by = "user"
        self._close()

    def close_by_operator(self, user_id: int, role: str):
        self.closed_by = f"{role}:{user_id}"
        self._close()
