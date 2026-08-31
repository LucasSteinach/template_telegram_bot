from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class IdMessage(Message):
    id: int
