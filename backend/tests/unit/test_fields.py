from datetime import datetime, timedelta, timezone

import pytest

from src.domain.db_filters.fields import (
    DatetimeFilterField,
    FilterField,
    NumericFilterField,
)
from src.domain.db_filters.operators import FieldOperator


class DummyField(FilterField):
    pass


def test_filter_field_not_implemented():
    field = DummyField()

    assert field.not_implemented()


def test_filter_field_operator_not_allowed():
    correct_case = DummyField(value=1)
    incorrect_case = DummyField(value=1)
    incorrect_case.operator = FieldOperator.NE

    assert correct_case.operator_not_allowed() is False
    assert incorrect_case.operator_not_allowed()


def test_filter_field_validate_common():
    with pytest.raises(ValueError):
        DummyField(value=1, operator=FieldOperator.NE)


def test_numeric_field_operator_between_chosen():
    field_with_between_operator = NumericFilterField(
        value=1, to=2, operator=FieldOperator.BTW
    )
    incorrect_case = NumericFilterField()

    assert incorrect_case.operator_between_chosen() is False
    assert field_with_between_operator.operator_between_chosen()


def test_numeric_field_validate():
    # field has btw operator and unset 'to' value
    with pytest.raises(
        ValueError, match="Value 'to' is required for BETWEEN operators"
    ):
        NumericFilterField(value=1, operator=FieldOperator.BTW)

    # 'value' greater than 'to'
    with pytest.raises(
        ValueError, match="The initial value cannot be greater than 'to'"
    ):
        NumericFilterField(value=2, to=1, operator=FieldOperator.BTW)


def test_datetime_field_operator_between_chosen():
    test_date = datetime.now(tz=timezone.utc)
    field_with_between_operator = DatetimeFilterField(
        value=test_date - timedelta(days=1), to=test_date, operator=FieldOperator.BTW
    )
    incorrect_case = DatetimeFilterField()

    assert incorrect_case.operator_between_chosen() is False
    assert field_with_between_operator.operator_between_chosen()


def test_datetime_field_validate():
    test_date = datetime.now(tz=timezone.utc)

    # field has btw operator and unset 'to' value
    with pytest.raises(
        ValueError, match="Value 'to' is required for BETWEEN operators"
    ):
        DatetimeFilterField(value=test_date, operator=FieldOperator.BTW)

    # 'value' greater than 'to'
    with pytest.raises(
        ValueError, match="The initial value cannot be greater than 'to'"
    ):
        DatetimeFilterField(
            value=test_date + timedelta(days=1),
            to=test_date,
            operator=FieldOperator.BTW,
        )
