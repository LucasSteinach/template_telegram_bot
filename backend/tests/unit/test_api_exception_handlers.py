from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse

from api.exception_handlers import (
    application_exception_handler,
    business_exception_handler,
)
from domain.exceptions import ApplicationException, BusinessLogicException
from domain.rules.rules import ApplicationRule, BusinessRule


class FakeBusinessRule(BusinessRule):
    _message = "rule is violated"

    def is_violated(self) -> bool:
        return True


class FakeApplicationRule(ApplicationRule):
    _message = "rule is violated"

    def is_violated(self) -> bool:
        return True


@pytest.mark.parametrize(
    ("handler", "exception", "status_code"),
    [
        (
            business_exception_handler,
            BusinessLogicException(FakeBusinessRule()),
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        ),
        (
            application_exception_handler,
            ApplicationException(FakeApplicationRule()),
            status.HTTP_406_NOT_ACCEPTABLE,
        ),
    ],
    ids=["business", "application"],
)
def test_exception_handler(handler, exception, status_code):
    with patch("api.exception_handlers.logger.warning") as logger_mock:
        response = handler(None, exception)

        logger_mock.assert_called_once()
        assert isinstance(response, JSONResponse)
        assert response.status_code == status_code
