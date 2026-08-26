from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.auth import AuthService, AuthUser
from src.dependencies.services import get_auth_service
from src.domain.entities.user import UserRole


async def _get_user(
    credentials: HTTPAuthorizationCredentials,
    auth_service: AuthService,
) -> AuthUser:
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized"
        )

    user = auth_service.decode_access_token(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized"
        )

    return user


async def get_auth_operator(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await _get_user(credentials, auth_service)
    if user.role not in [UserRole.OPERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    return user


async def get_auth_admin(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await _get_user(credentials, auth_service)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    return user
