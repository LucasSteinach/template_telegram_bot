class DomainException(Exception):
    def __init__(self, rule):
        self.rule = rule


class BusinessLogicException(DomainException):
    pass


class ApplicationException(DomainException):
    pass
