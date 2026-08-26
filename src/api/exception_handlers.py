import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.domain.exceptions import ApplicationException, BusinessLogicException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BusinessLogicException, business_exception_handler)
    app.add_exception_handler(ApplicationException, application_exception_handler)


def business_exception_handler(_: Request, exc: BusinessLogicException):
    logger.warning(
        "Business rule violated: %s",
        exc.rule.get_message,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.rule.get_message()}),
    )


def application_exception_handler(_: Request, exc: ApplicationException):
    logger.warning(
        "Application rule violated: %s",
        exc.rule.get_message,
    )
    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": exc.rule.get_message()}),
    )
