from aiogram.types import Message

from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard
from src.infrastructure.telegram.menu.helpers import get_menu_item


async def render_menu(message: Message, item_id: str = "root"):
    item = get_menu_item(item_id)
    keyboard = build_keyboard(item)

    await message.edit_text(text=item.message_text, reply_markup=keyboard)
