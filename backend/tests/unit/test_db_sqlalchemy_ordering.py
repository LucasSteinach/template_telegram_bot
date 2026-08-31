import pytest

from domain.db_filters.ordering import SortField
from infrastructure.database.models import UserModel
from infrastructure.database.sqlalchemy.ordering import SQLAlchemyOrderBy


class DummyOrderBy(SQLAlchemyOrderBy):
    bounded_model = UserModel

    allowed_fields: tuple[str] = ("username", "created_at")


@pytest.mark.parametrize(
    ("field_name", "error"),
    [
        (
            "wrong_field",
            f"Field 'wrong_field' does not exist in {DummyOrderBy.bounded_model.__name__}",
        ),
        (
            "id",
            f"Field 'id' is not allowed\nAllowed fields: {', '.join(DummyOrderBy(fields=[]).allowed_fields)}",
        ),
    ],
    ids=["field does not exist", "field is not allowed"],
)
def test_sqlalchemy_order_by_validation_errors(field_name, error):
    with pytest.raises(ValueError, match=error):
        DummyOrderBy(fields=[SortField(name=field_name)])


def test_sqlalchemy_order_by():
    field_name = "username"
    order_by = DummyOrderBy(fields=[SortField(name=field_name)])

    assert next((f.name for f in order_by.fields), None) == field_name
