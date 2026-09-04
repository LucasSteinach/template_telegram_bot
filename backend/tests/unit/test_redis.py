from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.redis.helpers import generate_message_hash
from infrastructure.redis.storage import RedisStorage


@pytest.mark.asyncio
async def test_redis_storage_disconnect():
    mock_redis = AsyncMock()
    storage = RedisStorage(redis=mock_redis)

    await storage.disconnect(close_connection_pool=False)

    mock_redis.aclose.assert_awaited_once_with(close_connection_pool=False)


@pytest.mark.asyncio
async def test_storage_main_menu_message_data(redis_storage, message, telegram_user):
    with patch("infrastructure.redis.storage.logger") as logger_mock:
        await redis_storage.set_main_menu_message_data(telegram_user.id, message)
        data = await redis_storage.get_main_menu_message_data(telegram_user.id)

    assert logger_mock.debug.call_count == 2
    assert isinstance(data, dict)
    assert data["message_text"] == message.text


@pytest.mark.asyncio
async def test_storage_refresh_token(redis_storage):
    with patch("infrastructure.redis.storage.logger") as logger_mock:
        await redis_storage.save_refresh_token(
            user_id=1, token_id="token_id", expire_sec=90
        )

        logger_mock.debug.assert_called_once()

        token_exists = await redis_storage.check_refresh_token(
            user_id=1, token_id="token_id"
        )

        assert token_exists

        await redis_storage.delete_refresh_token(user_id=1, token_id="token_id")
        await redis_storage.check_refresh_token(user_id=1, token_id="token_id")

        assert logger_mock.debug.call_count == 2


def test_generate_message_hash():
    data_1 = {
        "message_text": "test_text_1",
        "reply_markup": None,
    }
    data_2 = {
        "message_text": "test_text_2",
        "reply_markup": None,
    }

    hash_1 = generate_message_hash(**data_1)
    hash_2 = generate_message_hash(**data_1)

    assert hash_1 == hash_2

    hash_3 = generate_message_hash(**data_2)

    assert hash_3 != hash_1
