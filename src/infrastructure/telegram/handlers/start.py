import asyncio
import logging

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.application.dto.user_dto import RegisterUser
from src.container import Container
from src.infrastructure.telegram.handlers.actions.helpers import delete_messages
from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard
from src.infrastructure.telegram.keyboards.menu import get_menu_item
from src.infrastructure.telegram.keyboards.menu_constants import MENU

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, container: Container) -> None:
    dto = RegisterUser(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name or message.from_user.username,
    )

    async with container.session_factory() as session:
        use_case = container.register_user_use_case(session)
        user = await use_case.execute(dto)

    menu_message = await container.redis_storage.get_main_menu_message_data(
        message.from_user.id
    )
    keyboard = build_keyboard(get_menu_item("root"), "root")
    new_message_text = MENU.message_text

    if not menu_message:
        new_message_text = f"Hi, {user.full_name}!"

        answer = await message.answer(
            new_message_text,
            reply_markup=keyboard,
        )
        await container.redis_storage.set_main_menu_message_data(
            message.from_user.id, answer
        )
        await delete_messages(message, [message.message_id])

    else:
        if new_message_text == menu_message.get("message_text"):
            warning_message = await message.answer(
                f"If you don't see the menu, please contact support {container.settings.support_user.split(':')[1]}"
            )
            await asyncio.sleep(3)
            await delete_messages(
                message, [message.message_id, warning_message.message_id]
            )
            return

        try:
            edited_message = await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=menu_message.get("message_id"),
                text=new_message_text,
                reply_markup=keyboard,
            )
            await container.redis_storage.set_main_menu_message_data(
                message.from_user.id, edited_message
            )
        except TelegramBadRequest as e:
            logger.debug(e)

        await delete_messages(message, [message.message_id])
