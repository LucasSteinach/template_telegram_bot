import json

from aio_pika import Message, connect_robust
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustChannel,
    AbstractRobustConnection,
    DeliveryMode,
)

QUEUES = ("support_messages",)


class RabbitMQ:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def connect(self, queues: tuple[str] = QUEUES) -> None:
        self._connection = await connect_robust(self._url)
        self._channel = await self._connection.channel()

        for q in queues:
            await self._declare_queue(queue_name=q)

    async def _declare_queue(
        self, queue_name: str, durable: bool = True
    ) -> AbstractQueue:
        if self._channel is None:
            raise RuntimeError("RabbitMQ is not connected")

        return await self._channel.declare_queue(
            queue_name,
            durable=durable,
        )

    async def publish(
        self,
        queue_name: str,
        data: dict,
    ) -> None:

        if self._channel is None:
            raise RuntimeError("RabbitMQ is not connected")

        message = Message(
            body=json.dumps(data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await self._channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )

    async def consume(
        self,
        queue_name: str,
        handler,
    ) -> None:
        if self._channel is None:
            raise RuntimeError("RabbitMQ is not connected")

        queue = await self._declare_queue(queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                message: AbstractIncomingMessage

                async with message.process():
                    data = json.loads(message.body)

                    await handler(**data)

    async def close(self):
        if self._connection is not None:
            await self._connection.close()
