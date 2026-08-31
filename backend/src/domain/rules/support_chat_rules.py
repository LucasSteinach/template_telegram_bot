from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.domain.entities.user import UserRole
from src.domain.rules.rules import BusinessRule


class SupportChatExist(BusinessRule):
    _message = "chat not exist"

    chat: SupportChat | None

    def is_violated(self) -> bool:
        return self.chat is None


class UserOwnChat(BusinessRule):
    _message = "chat not exist"

    owner_id: int
    user_id: int

    def is_violated(self) -> bool:
        return self.owner_id != self.user_id


class ChatIsNotClosed(BusinessRule):
    _message = "chat closed"

    status: str

    def is_violated(self) -> bool:
        return self.status == ChatStatus.CLOSED


class WaitingAfterCreation(BusinessRule):
    _message = "status 'waiting' can only be after creation"

    status: str

    def is_violated(self) -> bool:
        return self.status != ChatStatus.CREATED


class IsOperator(BusinessRule):
    _message = "user is not an operator"

    role: str

    def is_violated(self) -> bool:
        return self.role not in [UserRole.OPERATOR, UserRole.ADMIN]
