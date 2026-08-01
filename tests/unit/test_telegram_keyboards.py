import pytest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from src.infrastructure.telegram.keyboards import inline_keyboard as ik
from src.infrastructure.telegram.keyboards import reply_keyboard as rk
from src.infrastructure.telegram.keyboards.dto import MENU


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
    button_1 = ik.create_back_button("some_path")
    button_2 = ik.create_back_button("path.subpath")

    assert isinstance(button_1, InlineKeyboardButton)
    assert isinstance(button_2, InlineKeyboardButton)
    assert button_1.callback_data == "menu:root"
    assert button_2.callback_data == "menu:path"


def test_has_button():
    kb = ik.build_keyboard(MENU, "root")
    assert ik.has_button(kb, next(c.button_text for c in MENU.children))
    assert not ik.has_button(kb, "incorrect_text")


def test_build_callback():
    # MenuItem(type="menu")
    item_1 = next(c for c in MENU.children if c.type == "menu")
    # MenuItem(type="action")
    item_2 = next(c for c in MENU.children if c.type == "action")

    callback = ik.build_callback(item_1, MENU.id)
    assert callback == ik.MenuCallback(path=item_1.id).pack()

    callback = ik.build_callback(item_2, item_2.id)
    assert callback == ik.AwaitedActionCallback(action=item_2.id).pack()


def test_build_keyboard():
    no_item_keyboard = ik.build_keyboard(None, "")  # noqa
    assert no_item_keyboard is None

    root_keyboard = ik.build_keyboard(MENU, "root")
    assert (
        next(
            (
                b
                for row in root_keyboard.inline_keyboard
                for b in row
                if b.text == ik.BACK_TEXT
            ),
            None,
        )
        is None
    )

    item_with_no_keyboard = next(c for c in MENU.children if len(c.children) == 0)
    keyboard = ik.build_keyboard(item_with_no_keyboard, item_with_no_keyboard.id)
    assert (
        next(
            (
                b
                for row in keyboard.inline_keyboard
                for b in row
                if b.text == ik.BACK_TEXT
            ),
            None,
        )
        is not None
    )

    not_root_item = next(c for c in MENU.children if len(c.children) != 0)
    keyboard = ik.build_keyboard(not_root_item, not_root_item.id)
    assert (
        next(
            (
                b
                for row in keyboard.inline_keyboard
                for b in row
                if b.text == ik.BACK_TEXT
            ),
            None,
        )
        is not None
    )
