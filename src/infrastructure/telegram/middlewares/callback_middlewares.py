from aiogram import BaseMiddleware


class CallbackLockMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.processing = set()

    async def __call__(self, handler, event, data):
        key = (
            event.from_user.id,
            event.message.message_id,
        )

        if key in self.processing:
            await event.answer("⏳ Processed..")
            return

        self.processing.add(key)

        try:
            await event.answer()
            return await handler(event, data)
        finally:
            self.processing.remove(key)
