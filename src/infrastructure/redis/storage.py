import json
import logging

from aiogram.types import Message
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisStorage:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _key(user_id: int, action: str) -> str:
        return f"user:{user_id}:{action}"

    async def get_main_menu_message_data(self, user_id: int) -> dict:
        action = "main_menu"

        value = await self.redis.get(self._key(user_id, action))
        logger.debug("Redis GET %s=%s", self._key(user_id, "main_menu"), value)
        return json.loads(value) if value else {}

    async def set_main_menu_message_data(self, user_id: int, message: Message) -> None:
        action = "main_menu"

        data = {
            "message_id": message.message_id,
            "message_text": message.text,
        }
        logger.debug(
            "Redis SET %s=%s", self._key(user_id, action), message.model_dump()
        )
        await self.redis.set(
            self._key(user_id, "main_menu"),
            json.dumps(data),
        )
