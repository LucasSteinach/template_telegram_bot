import fakeredis.aioredis
import pytest
import pytest_asyncio
from redis.asyncio import Redis

from src.infrastructure.redis.storage import RedisStorage


@pytest_asyncio.fixture
async def redis_client() -> Redis:
    redis = fakeredis.aioredis.FakeRedis()

    yield redis

    await redis.aclose()


@pytest.fixture
def redis_storage(redis_client):
    return RedisStorage(redis_client)
