import pytest

from src.domain.db_filters.base_filter import BaseFilter
from src.domain.db_filters.fields import NumericFilterField, StringFilterField
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.sqlalchemy.compatibility import (
    get_filter_field_type,
    is_field_compatible,
)


class DummyFilter(BaseFilter):
    bounded_model = UserModel

    str_field: StringFilterField = StringFilterField()
    int_field: NumericFilterField | None = None


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("str_field", StringFilterField),
        ("int_field", NumericFilterField),
    ],
)
def test_get_filter_field_type(field_name, expected):
    annotation = DummyFilter.model_fields[field_name].annotation

    assert get_filter_field_type(annotation) is expected


def test_get_filter_field_type_unsupported():
    annotation = str

    with pytest.raises(
        TypeError, match=f"Expected FilterField annotation, got {annotation!r}"
    ):
        get_filter_field_type(annotation)


def test_is_field_compatible():
    str_column = getattr(UserModel, "username", None)
    not_allowed_type = type(None)

    assert is_field_compatible(str_column, StringFilterField)
    assert not is_field_compatible(str_column, NumericFilterField)
    assert not is_field_compatible(str_column, not_allowed_type)
