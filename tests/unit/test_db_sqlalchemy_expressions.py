import pytest
from sqlalchemy import ColumnElement, and_, not_, or_

from src.domain.db_filters.fields import (
    FilterField,
    NumericFilterField,
    StringFilterField,
)
from src.domain.db_filters.operators import FieldOperator, LogicalOperator
from src.domain.db_filters.ordering import SortField
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.sqlalchemy.expressions import (
    filter_field_to_expression,
    filter_to_expressions,
    group_to_expression,
    order_by_to_expression,
)
from src.infrastructure.database.sqlalchemy.filters import FilterGroup, UserFilter
from src.infrastructure.database.sqlalchemy.ordering import SQLAlchemyOrderBy


def compile_expression(exp: ColumnElement):
    return str(exp.compile(compile_kwargs={"literal_binds": True}))


class DummyFilterField(FilterField):
    value: float | None = None
    operator: FieldOperator = FieldOperator.EQ.replace("q", "rror")
    allowed_operators = ("error",)


class DummyOrderBy(SQLAlchemyOrderBy):
    bounded_model = UserModel
    allowed_fields: tuple[str] = ("created_at",)
    fields: list[SortField] = [SortField(name="created_at")]  # noqa


def test_filter_field_not_implemented():
    expression = filter_field_to_expression(UserModel.username, StringFilterField())

    assert expression is None


def test_filter_field_to_expression_unsupported_operator():
    operator = "error"
    with pytest.raises(ValueError, match=f"Unsupported filter operator: {operator}"):
        filter_field_to_expression(UserModel.username, DummyFilterField(value=1.0))


@pytest.mark.parametrize(
    ["column", "field", "expected"],
    [
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.EQ),
            UserModel.id == 1.0,
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.NE),
            UserModel.id != 1.0,
        ),
        (
            UserModel.username,
            StringFilterField(value="name", operator=FieldOperator.LIKE),
            UserModel.username.like("%name%"),
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.GT),
            UserModel.id > 1.0,
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.GTE),
            UserModel.id >= 1.0,
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.LT),
            UserModel.id < 1.0,
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, operator=FieldOperator.LTE),
            UserModel.id <= 1.0,
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, to=2, operator=FieldOperator.BTW),
            and_(UserModel.id > 1.0, UserModel.id < 2.0),
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, to=2, operator=FieldOperator.BTWE),
            and_(UserModel.id >= 1.0, UserModel.id <= 2.0),
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, to=2, operator=FieldOperator.BTWEL),
            and_(UserModel.id >= 1.0, UserModel.id < 2.0),
        ),
        (
            UserModel.id,
            NumericFilterField(value=1, to=2, operator=FieldOperator.BTWER),
            and_(UserModel.id > 1.0, UserModel.id <= 2.0),
        ),
    ],
    ids=[
        "== (EQ)",
        "!= (NE)",
        "like",
        "> (GT)",
        ">= (GTE)",
        "< (LT)",
        "<= (LTE)",
        "< v < (BTW)",
        "<= v <= (BTWE)",
        "<= v < (BTWEL)",
        "< v <= (BTWER)",
    ],
)
def test_filter_field_to_expression(column, field, expected):
    expression = filter_field_to_expression(column, field)
    assert str(expression.compile(compile_kwargs={"literal_binds": True})) == str(
        expected.compile(compile_kwargs={"literal_binds": True})
    )


def test_filter_to_expression_not_implemented():
    expression = filter_to_expressions(UserFilter())

    assert expression == []


def test_filter_to_expression():
    f = UserFilter(
        username=StringFilterField(value="name"), id=NumericFilterField(value=1)
    )
    expressions = filter_to_expressions(f)

    assert isinstance(expressions, list)
    assert len(expressions) == 2


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        (
            {"children": []},
            [],
        ),
        (
            {"children": [UserFilter(), UserFilter()]},
            [],
        ),
        (
            {
                "children": [
                    UserFilter(
                        username=StringFilterField(value="name"),
                        id=NumericFilterField(value=1),
                    )
                ]
            },
            str(
                and_(
                    UserModel.username == "name",
                    UserModel.id == 1,
                ).compile(compile_kwargs={"literal_binds": True})
            ),
        ),
        (
            {
                "operator": LogicalOperator.OR,
                "children": [
                    UserFilter(id=NumericFilterField(value=1)),
                    UserFilter(
                        username=StringFilterField(value="name"),
                    ),
                ],
            },
            str(
                or_(UserModel.id == 1.0, UserModel.username == "name").compile(
                    compile_kwargs={"literal_binds": True}
                )
            ),
        ),
        (
            {
                "operator": LogicalOperator.NOT,
                "children": [UserFilter(id=NumericFilterField(value=1))],
            },
            str(
                not_(UserModel.id == 1.0).compile(
                    compile_kwargs={"literal_binds": True}
                )
            ),
        ),
    ],
    ids=[
        "empty_group",
        "children_with_no_expressions",
        "and-group",
        "or-group",
        "not-group",
    ],
)
def test_group_to_expression(kwargs, expected):
    group = FilterGroup(**kwargs)
    expression = group_to_expression(group)

    assert compile_expression(expression[0]) if expression else expression == expected


def test_order_by_to_expression_not_implemented():
    expression = order_by_to_expression(DummyOrderBy(fields=[]))

    assert expression == []


def test_order_by_to_expression():
    order_by = DummyOrderBy()
    expression = order_by_to_expression(order_by)

    assert len(expression) == len(order_by.fields)
    assert compile_expression(expression[0]) == compile_expression(
        UserModel.created_at.asc()
    )
