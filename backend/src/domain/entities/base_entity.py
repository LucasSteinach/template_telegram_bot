from pydantic import BaseModel

from src.domain.mixins import BusinessLogicValidationMixin


class Entity(BaseModel, BusinessLogicValidationMixin):
    pass
