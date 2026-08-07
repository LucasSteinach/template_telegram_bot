from abc import ABC, abstractmethod

from src.domain.entities.support_message import SupportMessage


class BaseSupportMessageRepository(ABC):
    @abstractmethod
    async def get_message(self, message_id: int) -> SupportMessage | None: ...

    @abstractmethod
    async def get_messages_by_chat(self, chat_id: int) -> list[SupportMessage]: ...

    @abstractmethod
    async def persist(self, message: SupportMessage) -> SupportMessage: ...
