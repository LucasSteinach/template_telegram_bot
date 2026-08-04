from unittest.mock import patch

import pytest

from src.infrastructure.redis.helpers import generate_message_hash


@pytest.mark.asyncio
async def test_storage_main_menu_message_data(redis_storage, message, user):
    with patch("src.infrastructure.redis.storage.logger") as logger_mock:
        await redis_storage.set_main_menu_message_data(user.id, message)
        data = await redis_storage.get_main_menu_message_data(user.id)

    assert logger_mock.debug.call_count == 2
    assert isinstance(data, dict)
    assert data["message_text"] == message.text


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
