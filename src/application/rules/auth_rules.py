from src.domain.rules.rules import ApplicationRule


class InvalidAccessToken(ApplicationRule):
    _message = "Invalid token"

    data: dict | None

    def is_violated(self) -> bool:
        return not self.data or self.data.get("type") != "access"


class InvalidRefreshToken(ApplicationRule):
    _message = "Invalid token"

    data: dict | None

    def is_violated(self) -> bool:
        return not self.data or self.data.get("type") != "access"
