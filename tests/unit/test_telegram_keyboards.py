from __future__ import annotations

import pytest

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from src.infrastructure.telegram.keyboards import inline_keyboard as ik
from src.infrastructure.telegram.keyboards import reply_keyboard as rk


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

    with pytest.raises(ValueError, match="input contains no buttons"):
        assert ik.inline_kb([])  # noqa

    keyboard = ik.inline_kb(buttons)

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.model_dump()["inline_keyboard"]) == len(buttons)


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
