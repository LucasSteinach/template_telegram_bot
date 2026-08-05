import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

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

logger = logging.getLogger(__name__)
router = Router(name="support")


@router.callback_query(AwaitedActionCallback.filter(F.action == ActionId.CHAT))
async def open_support_chat(callback: CallbackQuery, state: FSMContext):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )

    await callback.answer()
    await state.set_state(SupportState.chat)

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
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )

    last_message = await message.answer(
        text="Thank you! Glad to be helpful to you\nReturn to main menu...",
        reply_markup=ReplyKeyboardRemove(),
    )

    messages = (await state.get_data()).get("cleanup_messages")
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
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )

    await add_messages_to_cleanup(state, [message.message_id])
