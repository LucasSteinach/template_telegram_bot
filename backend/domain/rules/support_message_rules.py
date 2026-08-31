from domain.entities.support_message import SupportMessage
from domain.rules.rules import BusinessRule


class SupportMessageExist(BusinessRule):
    _message = "support message not exist"

    message: SupportMessage | None

    def is_violated(self) -> bool:
        return self.message is None


class ChatHasMessages(BusinessRule):
    _message = "no messages or chat not exist"

    messages: list[SupportMessage]

    def is_violated(self) -> bool:
        return len(self.messages) == 0
