import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.infrastructure.telegram.callbacks import ActionId, AwaitedActionCallback
from src.infrastructure.telegram.fsm_states import InputDataState
from src.infrastructure.telegram.handlers.actions.helpers import (
    add_messages_to_cleanup,
    delete_messages,
)
from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard
from src.infrastructure.telegram.keyboards.menu_constants import MENU

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(AwaitedActionCallback.filter(F.action == ActionId.INPUT_EXAMPLE))
async def input_data_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )
    await callback.answer()
    await state.set_state(InputDataState.waiting_data)
    message = await callback.message.answer("Send me your text")
    await add_messages_to_cleanup(
        state, [callback.message.message_id, message.message_id]
    )


@router.message(InputDataState.waiting_data)
async def process_input(
    message: Message,
    state: FSMContext,
):
    logger.debug(
        f"____________________current state: {await state.get_state()}____________________"
    )
    text = message.text
    last_message = await message.answer(f"✅Received data: {text}")
    await add_messages_to_cleanup(state, [message.message_id, last_message.message_id])
    messages = (await state.get_data()).get("cleanup_messages")
    await state.clear()
    await asyncio.sleep(5)

    await message.answer(
        "Main menu",
        reply_markup=build_keyboard(MENU, "root"),
    )
    await delete_messages(message, messages)
