import itertools

import pytest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from infrastructure.telegram.callbacks import AwaitedActionCallback, MenuCallback
from infrastructure.telegram.keyboards import inline_keyboard as ik
from infrastructure.telegram.keyboards import reply_keyboard as rk
from infrastructure.telegram.menu.menu import MENU


def test_inline_button():
    with pytest.raises(ValueError, match="button label required"):
        ik.InlineButton(
            text="",
            callback_data="some_data",
        )

    with pytest.raises(
        ValueError,
        match="At least one required: url, callback data etc. \n"
        "See docs https://docs.aiogram.dev/en/latest/api/types/inline_keyboard_button.html",
    ):
        ik.InlineButton(
            text="button_name",
        )

    with pytest.raises(ValueError, match="row must be greater or equal to 1"):
        ik.InlineButton(
            text="button_name",
            row=-1,
            callback_data="some_data",
        )

    with pytest.raises(ValueError, match="max button label length is 64"):
        ik.InlineButton(
            text="more_than_64_symbols_more_than_64_symbols_more_than_64_symbols_more_than_64_symbols",
            callback_data="some_data",
        )

    with pytest.raises(ValueError, match="max callback_data length is 64"):
        ik.InlineButton(
            text="button_name",
            callback_data="more_than_64_symbols_more_than_64_symbols_more_than_64_symbols_more_than_64_symbols",
        )

    dto_button = ik.InlineButton(
        text="button_name",
        callback_data="some_data",
    )

    button = ik.create_button(dto_button)

    assert isinstance(button, InlineKeyboardButton)
    assert button.text == "button_name"


def test_inline_keyboard():
    buttons = [
        ik.InlineButton(
            text="button_1",
            row=1,
            callback_data="cb_1",
        ),
        ik.InlineButton(
            text="button_2",
            row=2,
            callback_data="cb_2",
        ),
        ik.InlineButton(
            text="button_3",
            row=3,
            callback_data="cb_3",
        ),
    ]

    input_no_buttons = ik.inline_kb([])
    assert input_no_buttons is None

    keyboard = ik.inline_kb(buttons)

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == len(buttons)


def test_reply_button():
    with pytest.raises(ValueError, match="button label required"):
        rk.ReplyButton(
            text="",
        )

    with pytest.raises(
        ValueError,
        match="At most one must be used: url, callback data etc. \n"
        "See docs https://docs.aiogram.dev/en/latest/api/types/keyboard_button.html",
    ):
        rk.ReplyButton(
            text="button_name",
            request_contact=True,
            request_location=True,
        )

    with pytest.raises(ValueError, match="row must be greater or equal to 1"):
        rk.ReplyButton(
            text="button_name",
            row=-1,
        )

    with pytest.raises(ValueError, match="max button label length is 64"):
        rk.ReplyButton(
            text="more_than_64_symbols_more_than_64_symbols_more_than_64_symbols_more_than_64_symbols"
        )

    dto_button = rk.ReplyButton(
        text="button_name",
    )

    button = rk.create_button(dto_button)

    assert isinstance(button, KeyboardButton)
    assert button.text == "button_name"


def test_reply_keyboard():
    buttons = [
        rk.ReplyButton(
            text="button_1",
            row=1,
        ),
        rk.ReplyButton(
            text="button_2",
            row=2,
        ),
        rk.ReplyButton(
            text="button_3",
            row=3,
        ),
    ]

    with pytest.raises(ValueError, match="input contains no buttons"):
        assert rk.reply_kb([])

    keyboard = rk.reply_kb(buttons)

    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.model_dump()["keyboard"]) == len(buttons)


def test_create_back_button():
    back_button_for_root = ik.create_back_button(MENU.id)

    assert back_button_for_root is None

    back_button = ik.create_back_button(MENU.children[0].id)

    assert isinstance(back_button, InlineKeyboardButton)
    assert back_button.callback_data == MenuCallback(item_id=MENU.id).pack()


def test_has_button():
    kb = ik.build_keyboard(MENU)
    assert ik.has_button(kb, next(c.button_text for c in MENU.children))
    assert not ik.has_button(kb, "incorrect_text")


def test_build_callback():
    # menu
    menu_type_item = next(c for c in MENU.children if c.type == "menu")

    callback = ik.build_callback(menu_type_item)

    assert callback == MenuCallback(item_id=menu_type_item.id).pack()

    # action
    action_type_item = next(c for c in MENU.children if c.type == "action")

    callback = ik.build_callback(action_type_item)
    assert callback == AwaitedActionCallback(action=action_type_item.id).pack()


def test_build_keyboard():
    no_item_keyboard = ik.build_keyboard(None)

    assert no_item_keyboard is None

    root_keyboard = ik.build_keyboard(MENU)

    assert ik.has_button(root_keyboard, MENU.children[0].button_text)
    assert not ik.has_button(root_keyboard, ik.BACK_TEXT)

    item_with_no_children = next(c for c in MENU.children if len(c.children) == 0)
    keyboard = ik.build_keyboard(item_with_no_children)

    assert ik.has_button(keyboard, ik.BACK_TEXT)

    not_root_item_with_children = next(c for c in MENU.children if len(c.children) != 0)
    keyboard = ik.build_keyboard(not_root_item_with_children)

    assert (
        len(list(itertools.chain.from_iterable(keyboard.inline_keyboard)))
        == len(not_root_item_with_children.children) + 1
    )
