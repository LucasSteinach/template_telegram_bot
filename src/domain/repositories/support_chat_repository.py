from abc import ABC, abstractmethod

from src.domain.entities.support_chat import SupportChat


class BaseSupportChatRepository(ABC):
    @abstractmethod
    async def get_chat(self, chat_id: int) -> SupportChat | None: ...

    @abstractmethod
    async def get_active_chats(self) -> list[SupportChat]: ...

    @abstractmethod
    async def get_chats_by_user(self, user_id: int) -> list[SupportChat]: ...

    @abstractmethod
    async def get_closed_chats(self) -> list[SupportChat]: ...

    @abstractmethod
    async def persist(self, chat: SupportChat) -> SupportChat: ...
