import pytest

from src.domain.db_filters.fields import NumericFilterField, StringFilterField
from src.domain.db_filters.operators import LogicalOperator
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.sqlalchemy.filters import (
    FilterGroup,
    SQLAlchemyFilter,
    UserFilter,
)


class InvalidFilter(SQLAlchemyFilter):
    bounded_model = UserModel

    username: StringFilterField | None = StringFilterField()
    wrong_field: NumericFilterField | None = None


class IncompatibleColumnFilter(SQLAlchemyFilter):
    bounded_model = UserModel

    username: NumericFilterField | None = NumericFilterField()


def test_sqlalchemy_filter_not_implemented():
    f = UserFilter()

    assert f.not_implemented() is True


@pytest.mark.parametrize(
    ["error", "f"],
    [
        (
            f"Field 'wrong_field' does not exist in {InvalidFilter.bounded_model.__name__}",
            InvalidFilter,
        ),
        (
            f"Field 'username' is not compatible with {NumericFilterField.__name__}",
            IncompatibleColumnFilter,
        ),
    ],
)
def test_sqlalchemy_filter_validation_errors(error, f):
    with pytest.raises(ValueError, match=error):
        f()


def test_sqlalchemy_filter_validate():
    f = UserFilter(id=NumericFilterField())

    assert f.not_implemented() is False
    assert f.id is not None


@pytest.mark.parametrize(
    ["error", "children"],
    [
        (
            "NOT group must contain exactly one child with exactly one field",
            [
                UserFilter(),
                UserFilter(),
            ],
        ),
        (
            "NOT group filter must contain exactly one field",
            [
                UserFilter(
                    username=StringFilterField(value="name"),
                    full_name=StringFilterField(value="name"),
                )
            ],
        ),
    ],
    ids=["not the only child", "1 filter-child with not the only implemented field"],
)
def test_sqlalchemy_filter_group_validation_errors(error, children):
    with pytest.raises(ValueError, match=error):
        FilterGroup(operator=LogicalOperator.NOT, children=children)
