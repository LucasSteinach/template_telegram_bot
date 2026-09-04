from unittest.mock import patch

import pytest

from config import ROUTE

PATH = "api.auth"


@pytest.mark.asyncio
async def test_login(async_client, app, create_test_operator):

    response = await async_client.post(
        ROUTE.LOGIN, json={"email": "test@test.com", "password": "12345678"}
    )

    assert response.status_code == 200
    assert all(
        key in response.json()
        for key in ["access_token", "refresh_token", "expires_in"]
    )


@pytest.mark.asyncio
async def test_refresh(async_client, app, create_test_operator):
    refresh_token = (
        (
            await async_client.post(
                ROUTE.LOGIN, json={"email": "test@test.com", "password": "12345678"}
            )
        )
        .json()
        .get("refresh_token")
    )

    with (
        patch(f"{PATH}.logger.error") as logger_mock,
        patch(f"{PATH}.AuthService.refresh_session", side_effect=ValueError),
    ):
        response = await async_client.post(
            ROUTE.REFRESH, json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401
        logger_mock.assert_called_once()

    response = await async_client.post(
        ROUTE.REFRESH, json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    assert all(
        key in response.json()
        for key in ["access_token", "refresh_token", "expires_in"]
    )


@pytest.mark.asyncio
async def test_logout(async_client, app, create_test_operator):
    refresh_token = (
        (
            await async_client.post(
                ROUTE.LOGIN, json={"email": "test@test.com", "password": "12345678"}
            )
        )
        .json()
        .get("refresh_token")
    )

    with patch(f"{PATH}.AuthService.logout_session") as logout_session_mock:
        response = await async_client.post(
            ROUTE.LOGOUT, json={"refresh_token": refresh_token}
        )

        logout_session_mock.assert_awaited_once()
        assert response.status_code == 200
        assert response.json().get("detail") == "success"
