from pydantic import BaseModel

from src.domain.exceptions import ApplicationException, BusinessLogicException


class BaseRule(BaseModel):
    _message: str = "Rule is violated"

    def get_message(self) -> str:
        return self._message

    def is_violated(self) -> bool:
        pass

    def __str__(self):
        return self.get_message()


class BusinessRule(BaseRule):
    _message: str = "business rule is violated"


class ApplicationRule(BaseRule):
    _message: str = "application rule is violated"


def check_business_rule(rule: BusinessRule):
    if rule.is_violated():
        raise BusinessLogicException(rule)


def check_app_rule(rule: ApplicationRule):
    if rule.is_violated():
        raise ApplicationException(rule)
