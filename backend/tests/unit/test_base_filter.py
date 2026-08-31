import pytest
from pydantic import model_validator

from domain.db_filters.base_filter import BaseFilter
from infrastructure.database.models import UserModel


class DummyFilter(BaseFilter):
    bounded_model = UserModel

    id: int | None = None
    username: str | None = None

    @model_validator(mode="after")
    def validate_fields(self):
        return self


def test_base_filter_validate_fields():
    with pytest.raises(NotImplementedError):
        BaseFilter()


def test_base_filter_fields():
    f = DummyFilter(id=1, username="Test Username")

    assert isinstance(f.fields(), list)
    assert set(f.fields()) == set(f.model_fields)
    assert "bounded_model" not in f.fields()


def test_base_filter_not_implemented():
    f = DummyFilter(id=1, username="Test Username")
    all_none_filter = DummyFilter(id=None, username=None)

    assert f.not_implemented() is False
    assert all_none_filter.not_implemented() is True
