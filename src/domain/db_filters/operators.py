from enum import StrEnum


class FieldOperator(StrEnum):
    EQ = "eq"  # ==
    NE = "ne"  # !=
    LIKE = "like"  # LIKE
    GT = "gt"  # >
    GTE = "gte"  # >=
    LT = "lt"  # <
    LTE = "lte"  # <=

    BTW = "btw"  # < value < to
    BTWE = "btwe"  # <= value <= to
    BTWEL = "btwel"  # <= value < to
    BTWER = "btwer"  # < value <= to


class LogicalOperator(StrEnum):
    AND = "and"
    OR = "or"
    NOT = "not"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"
