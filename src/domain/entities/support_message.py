from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SupportMessage:
    chat_id: int
    author_id: int
    author_role: str
    text: str

    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
