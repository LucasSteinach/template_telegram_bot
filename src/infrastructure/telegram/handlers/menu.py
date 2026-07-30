from aiogram import Router
from aiogram.types import CallbackQuery, Message

from src.infrastructure.telegram.keyboards import inline_keyboard as ik

router = Router(name="menu")


async def render_menu(
    message: Message,
    path: str,
):
    match path:
        case "root":
            await message.edit_text("Main menu")
            keyboard = ik.top_level_kb.model_copy()
        case "option_1":
            await message.edit_text("Menu 'Option 1'")
            keyboard = ik.option_1_kb.model_copy()
        case "option_2":
            await message.edit_text("Menu 'Option 2'")
            keyboard = ik.option_2_kb.model_copy()
        case _:
            return

    if path != "root" and not ik.has_button(keyboard, ik.BACK_TEXT):
        back_button = ik.create_back_button(path)
        keyboard.inline_keyboard.append([back_button])

    await message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(ik.MenuCallback.filter())
async def menu_handler(
    callback: CallbackQuery,
    callback_data: ik.MenuCallback,
):
    await callback.answer()
    await render_menu(
        callback.message,
        callback_data.path,
    )
