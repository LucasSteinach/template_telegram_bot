from unittest.mock import ANY, AsyncMock

import pytest

from src.infrastructure.telegram.menu.constants import MENU, MenuItem
from src.infrastructure.telegram.menu.helpers import get_menu_item
from src.infrastructure.telegram.menu.menu import render_menu


def test_constants_menu_item(menu_item):
    button_labels = menu_item.button_labels
    children_button_texts_list = [c.button_text for c in menu_item.children]

    assert button_labels == children_button_texts_list


def test_helpers_get_menu_item():
    whole_menu = get_menu_item("root")
    assert whole_menu == MENU

    with pytest.raises(
        AttributeError, match="'NoneType' object has no attribute 'split'"
    ):
        get_menu_item("incorrect_path")

    item = get_menu_item(next(c for c in MENU.children).id)
    assert isinstance(item, MenuItem)


@pytest.mark.asyncio
async def test_render_menu(message):
    message.edit_text = AsyncMock()

    await render_menu(message, "root")

    message.edit_text.assert_awaited_once_with(text=MENU.message_text, reply_markup=ANY)
