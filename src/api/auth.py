import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.response import Message
from src.application.services.auth import AuthService, Login, RefreshRequest, Token
from src.application.usecases.operator_use_case import OperatorUseCase
from src.config import ROUTE
from src.dependencies.services import get_auth_service
from src.dependencies.usecases import get_operator_use_case

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


@router.post(ROUTE.LOGIN, response_model=Token)
async def login(
    req: Login,
    auth_service: AuthService = Depends(get_auth_service),
    uc: OperatorUseCase = Depends(get_operator_use_case),
) -> Token:
    operator = await uc.get_operator_by_email(req.email)
    auth_service.check_password(req.password, operator.password)

    (access_token, refresh_token, expires_in) = await auth_service.new_session(
        operator.id,
        operator.role,
    )

    return Token(
        access_token=access_token, refresh_token=refresh_token, expires_in=expires_in
    )


@router.post(ROUTE.REFRESH, response_model=Token)
async def refresh_session(
    req: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        (
            access_token,
            new_refresh_token,
            expires_in,
        ) = await auth_service.refresh_session(req.refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=expires_in,
        )
    except (ValueError, KeyError) as e:
        logger.error("Refresh failed: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post(ROUTE.LOGOUT)
async def logout(
    req: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    await auth_service.logout_session(req.refresh_token)
    return Message(detail="success")
