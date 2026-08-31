from pydantic import BaseModel

from domain.mixins import BusinessLogicValidationMixin


class Entity(BaseModel, BusinessLogicValidationMixin):
    pass
