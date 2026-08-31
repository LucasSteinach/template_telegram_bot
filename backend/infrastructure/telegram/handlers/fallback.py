from aiogram import Router
from aiogram.types import Message

router = Router(name="fallback")


@router.message()
async def delete_unhandled_messages(message: Message):
    await message.delete()
