from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from domain.db_filters.operators import FieldOperator


class FilterField(BaseModel):
    value: Any | None = None
    operator: FieldOperator = FieldOperator.EQ
    allowed_operators: ClassVar[list[FieldOperator]] = [FieldOperator.EQ]

    def not_implemented(self) -> bool:
        return self.value is None

    def operator_not_allowed(self) -> bool:
        return self.operator not in self.allowed_operators

    def validate_common(self):
        if self.operator_not_allowed():
            raise ValueError(
                f"Operator '{self.operator}' is not allowed for "
                f"{self.__class__.__name__}. "
                f"Allowed operators: {self.allowed_operators}"
            )

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        if self.not_implemented() is False:
            self.validate_common()
        return self


class StringFilterField(FilterField):
    value: str | None = None
    allowed_operators = [FieldOperator.EQ, FieldOperator.NE, FieldOperator.LIKE]


class NumericFilterField(FilterField):
    value: float | None = None
    to: float | None = None
    allowed_operators = [op for op in FieldOperator if op != FieldOperator.LIKE]

    def operator_between_chosen(self) -> bool:
        return self.operator in {
            FieldOperator.BTW,
            FieldOperator.BTWE,
            FieldOperator.BTWEL,
            FieldOperator.BTWER,
        }

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        if self.not_implemented() is True:
            return self

        self.validate_common()

        if self.operator_between_chosen() and self.to is None:
            raise ValueError("Value 'to' is required for BETWEEN operators")

        if (
            self.operator_between_chosen()
            and self.to is not None
            and self.value > self.to
        ):
            raise ValueError("The initial value cannot be greater than 'to'")

        return self


class DatetimeFilterField(FilterField):
    value: datetime | None = None
    to: datetime | None = None
    operator: FieldOperator = FieldOperator.GT

    allowed_operators = [
        op
        for op in FieldOperator
        if op
        not in {
            FieldOperator.EQ,
            FieldOperator.NE,
            FieldOperator.LIKE,
        }
    ]

    def operator_between_chosen(self) -> bool:
        return self.operator in {
            FieldOperator.BTW,
            FieldOperator.BTWE,
            FieldOperator.BTWEL,
            FieldOperator.BTWER,
        }

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        if self.not_implemented() is True:
            return self

        self.validate_common()

        if self.operator_between_chosen() and self.to is None:
            raise ValueError("Value 'to' is required for BETWEEN operators")

        if (
            self.operator_between_chosen()
            and self.to is not None
            and self.value > self.to
        ):
            raise ValueError("The initial value cannot be greater than 'to'")

        return self
