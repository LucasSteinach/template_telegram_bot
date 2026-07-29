from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    telegram_id: int
    username: str | None
    full_name: str
    created_at: datetime
