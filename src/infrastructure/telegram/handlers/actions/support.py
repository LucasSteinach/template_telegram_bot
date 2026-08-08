import asyncio
import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from src.container import Container
from src.domain.entities.support_chat import ChatStatus
from src.infrastructure.telegram.callbacks import ActionId, AwaitedActionCallback
from src.infrastructure.telegram.fsm_states import SupportState
from src.infrastructure.telegram.handlers.actions.helpers import (
    add_messages_to_cleanup,
    delete_messages,
)
from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard
from src.infrastructure.telegram.keyboards.reply_keyboard import (
    CLOSE_CHAT,
    ReplyButton,
    reply_kb,
)
from src.infrastructure.telegram.menu.constants import MENU
from src.utils.text import truncate

logger = logging.getLogger(__name__)
router = Router(name="support")


@router.callback_query(AwaitedActionCallback.filter(F.action == ActionId.CHAT))
async def open_support_chat(
    callback: CallbackQuery, state: FSMContext, container: Container
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )

    await callback.answer()
    await state.set_state(SupportState.chat)

    async with container.session_factory() as session:
        support_chat = await container.support_chat_uc(session).create_chat(
            callback.from_user.id
        )

    await state.update_data({"support_chat_id": support_chat.id})

    await callback.message.edit_reply_markup(reply_markup=None)

    message = await callback.message.answer(
        text="Write your message", reply_markup=reply_kb([ReplyButton(CLOSE_CHAT)])
    )

    await add_messages_to_cleanup(
        state, [callback.message.message_id, message.message_id]
    )


@router.message(SupportState.chat, F.text.casefold() == CLOSE_CHAT.casefold())
async def close_chat(
    message: Message,
    state: FSMContext,
    container: Container,
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )

    data = await state.get_data()
    support_chat_id = data.get("support_chat_id")
    messages = data.get("cleanup_messages")

    async with container.session_factory() as session:
        user = await container.user_uc(session).get_user(message.from_user.id)
        await container.support_chat_uc(session).close_chat(support_chat_id, user)

    last_message = await message.answer(
        text="Thank you! Glad to be helpful to you\nReturn to main menu...",
        reply_markup=ReplyKeyboardRemove(),
    )

    await state.clear()
    await asyncio.sleep(5)

    await message.answer(
        "Main menu",
        reply_markup=build_keyboard(MENU),
    )
    await delete_messages(
        message, messages + [message.message_id, last_message.message_id]
    )


@router.message(
    SupportState.chat,
)
async def process_message(
    message: Message,
    state: FSMContext,
    container: Container,
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )
    support_chat_id = (await state.get_data()).get("support_chat_id")

    async with container.session_factory() as session:
        user_uc = container.user_uc(session)
        support_chat_uc = container.support_chat_uc(session)
        support_message_uc = container.support_message_uc(session)

        user = await user_uc.get_user(message.from_user.id)
        support_chat = await support_chat_uc.get_chat(support_chat_id)
        support_chat.last_activity_at = datetime.now(tz=timezone.utc)

        await support_message_uc.save_message(
            support_chat_id, user.telegram_id, user.role, message.text
        )

        if support_chat.status == ChatStatus.CREATED:
            support_chat.topic = truncate(message.text)
            support_chat.waiting()

        await support_chat_uc.save_chat(support_chat)

    await add_messages_to_cleanup(state, [message.message_id])
