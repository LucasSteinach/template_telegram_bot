import fakeredis.aioredis
import pytest
import pytest_asyncio
from redis.asyncio import Redis
from testcontainers.community.rabbitmq import RabbitMqContainer

from infrastructure.redis.storage import RedisStorage


@pytest_asyncio.fixture
async def redis_client() -> Redis:
    redis = fakeredis.aioredis.FakeRedis()

    yield redis

    await redis.aclose()


@pytest.fixture
def redis_storage(redis_client):
    return RedisStorage(redis_client)


@pytest.fixture(scope="session")
def rabbitmq_url():
    with RabbitMqContainer("rabbitmq:3.11") as rabbit:
        params = rabbit.get_connection_params()
        url = f"amqp://{params.credentials.username}:{params.credentials.password}@{params.host}:{params.port}/"

        yield url
