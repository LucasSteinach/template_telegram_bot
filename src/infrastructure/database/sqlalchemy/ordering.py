from pydantic import model_validator

from src.domain.db_filters.ordering import BaseOrderBy
from src.infrastructure.database.models import (
    SupportChatModel,
    SupportMessageModel,
    UserModel,
)


class SQLAlchemyOrderBy(BaseOrderBy):
    @model_validator(mode="after")
    def validate_fields(self):
        if self.not_implemented():
            return self

        for field in self.fields:
            if not getattr(self.bounded_model, field.name, None):
                raise ValueError(
                    f"Field '{field.name}' does not exist "
                    f"in {self.bounded_model.__name__}"
                )
            if field.name not in self.allowed_fields:
                raise ValueError(
                    f"Field '{field.name}' is not allowed\n"
                    f"Allowed fields: {', '.join(self.allowed_fields)}"
                )

        return self


class UserOrderBy(SQLAlchemyOrderBy):
    bounded_model = UserModel

    allowed_fields: tuple[str] = ("username", "full_name", "created_at")


class SupportChatOrderBy(SQLAlchemyOrderBy):
    bounded_model = SupportChatModel

    allowed_fields: tuple[str] = ("created_at", "last_activity_at", "closed_at")


class SupportMessageOrderBy(SQLAlchemyOrderBy):
    bounded_model = SupportMessageModel

    allowed_fields: tuple[str] = ("created_at",)
