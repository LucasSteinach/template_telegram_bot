from typing import Self

from pydantic import BaseModel, model_validator

from src.domain.db_filters.base_filter import BaseFilter
from src.domain.db_filters.fields import NumericFilterField, StringFilterField
from src.domain.db_filters.operators import LogicalOperator
from src.infrastructure.database.models import (
    SupportChatModel,
    SupportMessageModel,
    UserModel,
)
from src.infrastructure.database.sqlalchemy.compatibility import (
    get_filter_field_type,
    is_field_compatible,
)


class SQLAlchemyFilter(BaseFilter):
    @model_validator(mode="after")
    def validate_fields(self):
        if self.not_implemented():
            return self

        for field_name, field_info in self.model_fields.items():
            column = getattr(self.bounded_model, field_name, None)

            if column is None:
                raise ValueError(
                    f"Field '{field_name}' does not exist "
                    f"in {self.bounded_model.__name__}"
                )

            filter_field_type = get_filter_field_type(field_info.annotation)

            if not is_field_compatible(
                column,
                filter_field_type,
            ):
                raise ValueError(
                    f"Field '{field_name}' is not compatible with "
                    f"{filter_field_type.__name__}"
                )

        return self


class UserFilter(SQLAlchemyFilter):
    bounded_model = UserModel

    username: StringFilterField | None = None
    full_name: StringFilterField | None = None
    role: StringFilterField | None = None
    id: NumericFilterField | None = None


class SupportChatFilter(SQLAlchemyFilter):
    bounded_model = SupportChatModel

    user_id: NumericFilterField | None = None
    operator_id: NumericFilterField | None = None
    status: StringFilterField | None = None


class SupportMessageFilter(SQLAlchemyFilter):
    bounded_model = SupportMessageModel

    chat_id: NumericFilterField | None = None
    author_id: NumericFilterField | None = None
    author_role: StringFilterField | None = None


class FilterGroup(BaseModel):
    operator: LogicalOperator = LogicalOperator.AND
    children: list[SQLAlchemyFilter, "FilterGroup"]

    def not_group_validate(self):
        if len(self.children) != 1:
            raise ValueError(
                "NOT group must contain exactly one child with exactly one field"
            )

        child = self.children[0]
        if isinstance(child, SQLAlchemyFilter):
            implemented_fields = [
                field_name
                for field_name in child.model_fields
                if getattr(child, field_name) is not None
            ]

            if len(implemented_fields) != 1:
                raise ValueError("NOT group filter must contain exactly one field")

    @model_validator(mode="after")
    def validate_children(self) -> Self:
        if self.operator == LogicalOperator.NOT:
            self.not_group_validate()

        return self
