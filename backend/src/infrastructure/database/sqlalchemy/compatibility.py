from typing import get_args

from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.types import TypeEngine

from src.domain.db_filters.fields import (
    DatetimeFilterField,
    FilterField,
    NumericFilterField,
    StringFilterField,
)

FILTER_FIELD_TYPES: dict[
    type[FilterField],
    tuple[type[TypeEngine], ...],
] = {
    StringFilterField: (String, Text),
    NumericFilterField: (Integer, BigInteger, Float, Numeric),
    DatetimeFilterField: (DateTime, Date),
}


def get_filter_field_type(
    annotation,
) -> type[FilterField]:
    if isinstance(annotation, type) and issubclass(annotation, FilterField):
        return annotation

    for type_ in get_args(annotation):
        if isinstance(type_, type) and issubclass(type_, FilterField):
            return type_

    raise TypeError(f"Expected FilterField annotation, got {annotation!r}")


def is_field_compatible(
    column,
    filter_field_type: type[FilterField],
) -> bool:
    column_type = column.property.columns[0].type

    allowed_types = FILTER_FIELD_TYPES.get(filter_field_type)

    if allowed_types is None:
        return False

    return isinstance(column_type, allowed_types)
