from fastapi import Request

from src.application.services.auth import AuthService
from src.application.services.rabbitmq import RabbitMQ


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.container.auth_service()


def get_rabbitmq(request: Request) -> RabbitMQ:
    return request.app.state.container.rabbitmq
