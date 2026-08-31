from src.domain.entities.operator import Operator
from src.domain.rules.rules import BusinessRule


class OperatorExist(BusinessRule):
    _message = "operator not exist"

    operator: Operator | None

    def is_violated(self) -> bool:
        return self.operator is None
