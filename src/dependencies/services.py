from fastapi import Request

from src.application.services.auth import AuthService


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.container.auth_service()
