from typing import ClassVar

from pydantic import BaseModel, model_validator


class BaseFilter(BaseModel):
    bounded_model: ClassVar[type[BaseModel]]

    def fields(self) -> list[str]:
        return list(self.model_fields)

    def not_implemented(self) -> bool:
        return all(
            getattr(self, field_name) is None for field_name in self.model_fields
        )

    @model_validator(mode="after")
    def validate_fields(self):
        raise NotImplementedError
