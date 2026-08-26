from src.domain.rules.rules import BusinessRule, check_business_rule


class BusinessLogicValidationMixin:
    @staticmethod
    def check_rule(rule: BusinessRule):
        check_business_rule(rule)
