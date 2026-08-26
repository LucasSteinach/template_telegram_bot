from dataclasses import field
from datetime import datetime, timezone

from src.domain.entities.base_entity import Entity


class SupportMessage(Entity):
    chat_id: int
    author_id: int
    author_role: str
    text: str

    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
