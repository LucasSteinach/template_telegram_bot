from unittest.mock import patch

import pytest
from fastapi import HTTPException

from application.services.auth import AuthService, AuthUser
from dependencies.auth import _get_user, get_auth_admin, get_auth_operator


class FakeAuthService(AuthService):
    def __init__(self):
        super().__init__("secret" * 6, 10, 20, None)


@pytest.mark.asyncio
async def test_get_user(fake_jwt_credentials):
    with pytest.raises(HTTPException, match="unauthorized"):
        await _get_user(None, None)

    service = FakeAuthService()
    user = await _get_user(fake_jwt_credentials(), service)

    assert isinstance(user, AuthUser)

    with (
        patch("dependencies.auth.AuthService.decode_access_token", return_value=None),
        pytest.raises(HTTPException, match="unauthorized"),
    ):
        await _get_user(fake_jwt_credentials(), service)


@pytest.mark.asyncio
async def test_get_auth_operator(fake_jwt_credentials):
    service = FakeAuthService()

    with pytest.raises(HTTPException, match="forbidden"):
        await get_auth_operator(fake_jwt_credentials(role="user"), service)

    operator = await get_auth_operator(fake_jwt_credentials(), service)

    assert isinstance(operator, AuthUser)


@pytest.mark.asyncio
async def test_get_auth_admin(fake_jwt_credentials):
    service = FakeAuthService()

    with pytest.raises(HTTPException, match="forbidden"):
        await get_auth_admin(fake_jwt_credentials(), service)

    admin = await get_auth_admin(fake_jwt_credentials(role="admin"), service)

    assert isinstance(admin, AuthUser)
