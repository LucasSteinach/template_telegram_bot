import pytest

from domain.exceptions import BusinessLogicException
from domain.mixins import BusinessLogicValidationMixin
from domain.rules.rules import BusinessRule


class FakeMixin(BusinessLogicValidationMixin):
    pass


class FakeRule(BusinessRule):
    _message = "rule was violated"

    def is_violated(self) -> bool:
        return True


def test_check_rule():
    mixin = FakeMixin()

    with pytest.raises(BusinessLogicException, match="rule was violated"):
        mixin.check_rule(FakeRule())
