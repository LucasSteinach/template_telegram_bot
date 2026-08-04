from unittest.mock import ANY, AsyncMock

import pytest

from src.infrastructure.telegram.keyboards.menu import get_menu_item, render_menu
from src.infrastructure.telegram.keyboards.menu_constants import MENU, MenuItem


def test_menu_item(menu_item):
    button_labels = menu_item.button_labels
    children_button_texts_list = [c.button_text for c in menu_item.children]

    assert button_labels == children_button_texts_list


def test_get_menu_item():
    whole_menu = get_menu_item("root")
    assert whole_menu == MENU

    wrong_item_path = get_menu_item("incorrect_path")
    assert wrong_item_path is None

    item = get_menu_item(next(c for c in MENU.children).id)
    assert isinstance(item, MenuItem)


@pytest.mark.asyncio
async def test_render_menu(message):
    message.edit_text = AsyncMock()

    await render_menu(message, "root")

    message.edit_text.assert_awaited_once_with(text=MENU.message_text, reply_markup=ANY)
