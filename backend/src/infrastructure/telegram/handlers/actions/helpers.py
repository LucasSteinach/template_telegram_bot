import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def add_messages_to_cleanup(state: FSMContext, message_ids: list[int]):
    data = await state.get_data()
    await state.update_data(
        cleanup_messages=data.get("cleanup_messages", []) + message_ids
    )


async def delete_messages(
    message: Message,
    message_ids: list[int],
) -> None:
    for message_id in message_ids:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=message_id,
            )
        except TelegramBadRequest as e:
            logger.debug(e)
