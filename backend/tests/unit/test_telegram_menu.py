from unittest.mock import ANY, AsyncMock

import pytest

from domain.exceptions import ApplicationException
from infrastructure.telegram.handlers.menu import render_menu
from infrastructure.telegram.menu.helpers import get_menu_item
from infrastructure.telegram.menu.menu import MENU, MenuItem, validate_menu_ids


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


def test_validate_menu_ids():
    duplicate_id = "duplicate_id"
    item = MenuItem(
        id="unique_id",
        message_text="message_text",
        button_text="",
        type="menu",
        children=[
            MenuItem(
                id=duplicate_id,
                message_text="message_text",
                button_text="",
                type="menu",
            ),
            MenuItem(
                id=duplicate_id,
                message_text="message_text",
                button_text="",
                type="menu",
            ),
        ],
    )

    with pytest.raises(
        ApplicationException, match=f"Duplicate menu item ids: {duplicate_id}"
    ):
        validate_menu_ids(item)
