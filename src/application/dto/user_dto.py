from dataclasses import dataclass


@dataclass
class RegisterUser:
    telegram_id: int
    username: str | None
    full_name: str
