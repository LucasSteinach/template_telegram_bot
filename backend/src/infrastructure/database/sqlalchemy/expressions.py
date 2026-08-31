from typing import Any

from sqlalchemy import ColumnElement, and_, not_, or_
from sqlalchemy.orm import InstrumentedAttribute

from src.domain.db_filters.fields import FilterField
from src.domain.db_filters.operators import (
    FieldOperator,
    LogicalOperator,
    SortDirection,
)
from src.infrastructure.database.sqlalchemy.filters import FilterGroup, SQLAlchemyFilter
from src.infrastructure.database.sqlalchemy.ordering import SQLAlchemyOrderBy


def filter_field_to_expression(
    column: InstrumentedAttribute[Any],
    field: FilterField,
) -> ColumnElement[bool] | None:
    if field.not_implemented():
        return None

    match field.operator:
        case FieldOperator.EQ:
            return column == field.value
        case FieldOperator.NE:
            return column != field.value
        case FieldOperator.LIKE:
            return column.like(f"%{field.value}%")
        case FieldOperator.GT:
            return column > field.value
        case FieldOperator.GTE:
            return column >= field.value
        case FieldOperator.LT:
            return column < field.value
        case FieldOperator.LTE:
            return column <= field.value

        case FieldOperator.BTW:
            return and_(
                column > field.value,
                column < field.to,
            )
        case FieldOperator.BTWE:
            return and_(
                column >= field.value,
                column <= field.to,
            )
        case FieldOperator.BTWEL:
            return and_(
                column >= field.value,
                column < field.to,
            )
        case FieldOperator.BTWER:
            return and_(
                column > field.value,
                column <= field.to,
            )

        case _:
            raise ValueError(f"Unsupported filter operator: {field.operator}")


def filter_to_expressions(f: SQLAlchemyFilter) -> list[ColumnElement[bool]]:
    expressions = []

    if f.not_implemented():
        return expressions

    for field_name in f.fields():
        field = getattr(f, field_name, None)

        if field is None or field.not_implemented():
            continue

        column = getattr(f.bounded_model, field_name)

        expressions.append(filter_field_to_expression(column, field))

    return expressions


def group_to_expression(group: FilterGroup) -> list[ColumnElement[bool]]:
    expressions = []

    for child in group.children:
        expression = (
            group_to_expression(child)
            if isinstance(child, FilterGroup)
            else filter_to_expressions(child)
        )

        if expression is not None:
            expressions.extend(expression)

    if not expressions:
        return []

    match group.operator:
        case LogicalOperator.AND:
            return [and_(*expressions)]

        case LogicalOperator.OR:
            return [or_(*expressions)]

        case LogicalOperator.NOT:
            return [not_(*expressions)]


def order_by_to_expression(
    order_by: SQLAlchemyOrderBy,
) -> list[ColumnElement[bool]]:
    expressions = []

    if order_by.not_implemented():
        return []

    for field in order_by.fields:
        column: ColumnElement = getattr(order_by.bounded_model, field.name)
        expressions.append(
            column.desc() if field.direction == SortDirection.DESC else column.asc()
        )

    return expressions
