import re
import string
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from redis import RedisError

from application.services.auth import (
    AuthService,
    AuthUser,
    create_tokens,
    decode,
    hash_password,
)
from domain.exceptions import ApplicationException

DATA = {
    "id": 1,
    "data": {
        "role": "user",
    },
    "secret": "1" * 32,
    "access_exp_sec": 10,
    "refresh_exp_sec": 20,
}


def test_create_and_decode_tokens():
    access_token, refresh_token, exp_sec = create_tokens(
        str(DATA["id"]), DATA["data"], DATA["secret"]
    )

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    assert exp_sec == 900

    no_data = decode("", DATA["secret"])

    assert no_data is None

    decoded_data = decode(access_token, DATA["secret"])

    assert decoded_data.get("role") == "user"


def test_auth_service_decode_access_token():
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], None
    )

    with pytest.raises(ApplicationException, match="Invalid token"):
        service.decode_access_token("wrong_token")

    access_token, refresh_token, _ = create_tokens(
        str(DATA["id"]), DATA["data"], DATA["secret"]
    )

    with pytest.raises(ApplicationException, match="Invalid token"):
        service.decode_access_token(refresh_token)

    user = service.decode_access_token(access_token)

    assert isinstance(user, AuthUser)
    assert user.id == DATA["id"]


def test_auth_service_decode_refresh_token():
    redis = MagicMock()
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], redis
    )
    access_token, refresh_token, _ = create_tokens(
        str(DATA["id"]), DATA["data"], DATA["secret"]
    )

    with pytest.raises(ApplicationException, match="Invalid token"):
        service.decode_refresh_token(access_token)

    user = service.decode_refresh_token(refresh_token)

    assert isinstance(user, AuthUser)
    assert user.id == DATA["id"]


@pytest.mark.asyncio
async def test_auth_service_new_session():
    redis = MagicMock()
    redis.save_refresh_token = AsyncMock()
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], redis
    )

    result = await service.new_session(DATA["id"], DATA["data"]["role"])

    redis.save_refresh_token.assert_awaited_once()
    assert isinstance(result, tuple)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_auth_service_refresh_session():
    path = "application.services.auth"
    redis = MagicMock()
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], redis
    )
    access_token, refresh_token, _ = create_tokens(
        str(DATA["id"]), DATA["data"], DATA["secret"]
    )

    with pytest.raises(ApplicationException, match="Invalid token"):
        await service.refresh_session(access_token)

    service.decode_refresh_token = MagicMock()
    no_token_id_payload = {}
    with patch(f"{path}.decode", new_callable=MagicMock()) as decode_mock:
        decode_mock.return_value.get = MagicMock(return_value=no_token_id_payload)

        with pytest.raises(
            ApplicationException, match=re.escape("Missing token identifier (jti)")
        ):
            await service.refresh_session(refresh_token)

        decode_mock.assert_called_once()
        assert decode_mock.return_value.get.call_count == 2

    invalid_session_payload = {"jti": "1"}
    redis.check_refresh_token = AsyncMock(return_value=False)
    with patch(f"{path}.decode", new_callable=MagicMock()) as decode_mock:
        decode_mock.return_value.get = MagicMock(return_value=invalid_session_payload)

        with pytest.raises(
            ApplicationException, match="Refresh token revoked or expired"
        ):
            await service.refresh_session(refresh_token)

        decode_mock.assert_called_once()
        decode_mock.return_value.get.assert_called_once()

    valid_session_payload = {"jti": "1"}
    redis.check_refresh_token = AsyncMock(return_value=True)
    redis.delete_refresh_token = AsyncMock()
    service.new_session = AsyncMock()
    with patch(f"{path}.decode", new_callable=MagicMock()) as decode_mock:
        decode_mock.return_value.get = MagicMock(return_value=valid_session_payload)

        await service.refresh_session(refresh_token)

        decode_mock.assert_called_once()
        decode_mock.return_value.get.assert_called_once()
        redis.check_refresh_token.assert_awaited_once()
        redis.delete_refresh_token.assert_awaited_once()
        service.new_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_logout_session():
    path = "application.services.auth"
    redis = MagicMock()
    redis.delete_refresh_token = AsyncMock()
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], redis
    )
    access_token, refresh_token, _ = create_tokens(
        str(DATA["id"]), DATA["data"], DATA["secret"]
    )

    invalid_token_or_no_payload = {}
    with (
        patch(
            f"{path}.decode", return_value=invalid_token_or_no_payload
        ) as decode_mock,
        patch(f"{path}.logger") as logger_mock,
    ):
        logger_mock.warning = MagicMock()

        await service.logout_session(access_token)

        decode_mock.assert_called_once()
        redis.delete_refresh_token.assert_not_awaited()
        logger_mock.warning.assert_not_called()

    with (
        patch(f"{path}.decode", side_effect=RedisError) as decode_mock,
        patch(f"{path}.logger") as logger_mock,
    ):
        logger_mock.warning = MagicMock()

        await service.logout_session(refresh_token)

        decode_mock.assert_called_once()
        redis.delete_refresh_token.assert_not_awaited()
        logger_mock.warning.assert_called_once()

    valid_payload = {"data": {"jti": "1"}, "id_": DATA["id"], "type": "refresh"}
    with (
        patch(f"{path}.decode", return_value=valid_payload) as decode_mock,
        patch(f"{path}.logger") as logger_mock,
    ):
        logger_mock.warning = MagicMock()

        await service.logout_session(refresh_token)

        decode_mock.assert_called_once()
        redis.delete_refresh_token.assert_awaited_once()
        logger_mock.warning.assert_not_called()


def test_auth_service_generate_password():
    min_length = 3
    low_length = 2
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], None
    )

    password = service.generate_password(low_length)

    assert isinstance(password, str)
    assert any(letter in string.ascii_uppercase for letter in password)
    assert any(letter in string.ascii_lowercase for letter in password)
    assert any(digit in string.digits for digit in password)
    assert len(password) == min_length

    length = 5

    password = service.generate_password(length)
    assert len(password) == length


def test_auth_service_check_password_and_hash_password():
    redis = MagicMock()
    service = AuthService(
        DATA["secret"], DATA["access_exp_sec"], DATA["refresh_exp_sec"], redis
    )
    password = "12341234"
    wrong_password = "1234"

    with pytest.raises(HTTPException):
        service.check_password(wrong_password, hash_password(password))

    assert service.check_password(password, hash_password(password)) is None
