import json
import logging

from aiogram.types import Message
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisStorage:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def disconnect(self, close_connection_pool=True):
        await self.redis.aclose(close_connection_pool=close_connection_pool)

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
        logger.debug("Redis SET %s=%s", self._key(user_id, action), json.dumps(data))
        await self.redis.set(
            self._key(user_id, "main_menu"),
            json.dumps(data),
        )

    async def save_refresh_token(
        self, user_id: int, token_id: str, expire_sec: int
    ) -> None:
        action = "refresh"
        key = self._key(user_id, f"{action}:{token_id}")

        await self.redis.set(key, "1", ex=expire_sec)
        logger.debug("Redis SET %s with TTL %s", key, expire_sec)

    async def check_refresh_token(self, user_id: int, token_id: str) -> bool:
        action = "refresh"
        key = self._key(user_id, f"{action}:{token_id}")

        exists = await self.redis.exists(key)
        return bool(exists)

    async def delete_refresh_token(self, user_id: int, token_id: str) -> None:
        action = "refresh"
        key = self._key(user_id, f"{action}:{token_id}")

        await self.redis.delete(key)
        logger.debug("Redis DEL %s", key)
