from typing import ClassVar

from pydantic import BaseModel, model_validator

from domain.db_filters.operators import SortDirection


class SortField(BaseModel):
    name: str
    direction: SortDirection = SortDirection.ASC


class BaseOrderBy(BaseModel):
    bounded_model: ClassVar[type[BaseModel]]

    allowed_fields: tuple[str]

    fields: list[SortField]

    def not_implemented(self) -> bool:
        return not self.fields

    @model_validator(mode="after")
    def validate_fields(self):
        raise NotImplementedError
