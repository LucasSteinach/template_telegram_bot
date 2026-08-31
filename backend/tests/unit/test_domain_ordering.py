import pytest
from pydantic import model_validator

from domain.db_filters.operators import SortDirection
from domain.db_filters.ordering import BaseOrderBy, SortField
from infrastructure.database.models import UserModel


class DummyOrderBy(BaseOrderBy):
    bounded_model = UserModel

    allowed_fields: tuple[str] = ("created_at", "username")

    fields: list[SortField] = []  # noqa

    @model_validator(mode="after")
    def validate_fields(self):
        return self


def test_base_order_by_validate_fields():
    with pytest.raises(NotImplementedError):
        BaseOrderBy(fields=[], allowed_fields=("test_field",))


def test_base_order_by_not_implemented():
    implemented_order_by = DummyOrderBy(fields=[SortField(name="username")])
    no_fields_order_by = DummyOrderBy()

    assert implemented_order_by.not_implemented() is False
    assert implemented_order_by.fields[-1].direction == SortDirection.ASC
    assert no_fields_order_by.not_implemented() is True
