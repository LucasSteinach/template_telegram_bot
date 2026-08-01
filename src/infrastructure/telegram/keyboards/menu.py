import logging

from aiogram.types import Message

from src.infrastructure.telegram.keyboards.dto import MENU, MenuItem
from src.infrastructure.telegram.keyboards.inline_keyboard import build_keyboard

logger = logging.getLogger(__name__)


def get_menu_item(path: str) -> MenuItem | None:
    item = MENU

    if path == "root":
        return item

    logger.debug("Searching menu path: %s", path)
    for part in path.split("."):
        if part not in [c.id for c in item.children]:
            return None

        item = next(c for c in item.children if c.id == part)

    return item


async def render_menu(message: Message, path: str):
    item = get_menu_item(path)
    keyboard = build_keyboard(item, path)

    await message.edit_text(text=item.message_text, reply_markup=keyboard)
