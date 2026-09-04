import asyncio
from unittest.mock import AsyncMock

import pytest

from application.services.rabbitmq import RabbitMQ


@pytest.mark.asyncio
async def test_connect(rabbitmq_url):
    service = RabbitMQ(url=rabbitmq_url)

    assert service._connection is None
    assert service._channel is None

    with pytest.raises(RuntimeError, match="RabbitMQ is not connected"):
        await service._declare_queue("test_queue")

    await service.connect(("test_queue",))

    assert service._connection is not None
    assert service._channel is not None

    await service.close()

    assert service._connection.is_closed
    assert service._channel.is_closed


@pytest.mark.asyncio
async def test_publish_consume(rabbitmq_url):
    service = RabbitMQ(url=rabbitmq_url)
    queue = "test_queue"
    handler = AsyncMock()

    data = {
        1: "test",
        2: "text",
    }

    with pytest.raises(RuntimeError, match="RabbitMQ is not connected"):
        await service.publish(queue, {})

    with pytest.raises(RuntimeError, match="RabbitMQ is not connected"):
        await service.consume(queue, lambda x: x)

    await service.connect((queue,))

    await service.publish(queue, data)
    consume_task = asyncio.create_task(service.consume(queue, handler))
    await asyncio.sleep(0.1)

    consume_task.cancel()
    # try:
    #     await consume_task
    # except asyncio.CancelledError:
    #     pass

    handler.assert_awaited_once()

    await service.close()
