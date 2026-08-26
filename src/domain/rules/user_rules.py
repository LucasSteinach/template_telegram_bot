from src.domain.entities.user import User
from src.domain.rules.rules import BusinessRule


class UserExist(BusinessRule):
    _message = "user not exist"

    user: User | None

    def is_violated(self) -> bool:
        return self.user is None
