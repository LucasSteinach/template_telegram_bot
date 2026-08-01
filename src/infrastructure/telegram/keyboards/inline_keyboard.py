import logging
from dataclasses import dataclass, fields
from typing import Literal

import aiogram.types as t
from aiogram.filters.callback_data import CallbackData

from src.infrastructure.telegram.keyboards.dto import MENU, MenuItem

logger = logging.getLogger(__name__)

BACK_TEXT = "⬅ Back"


class AwaitedActionCallback(CallbackData, prefix="action"):
    action: str


class MenuCallback(CallbackData, prefix="menu"):
    path: str


@dataclass
class InlineButton:
    text: str  # label

    row: int = 1

    icon_custom_emoji_id: str | None = None
    style: Literal["danger", "success", "primary"] | None = None  # red, green or blue

    url: str | None = None
    callback_data: str | None = None
    web_app: t.WebAppInfo | None = None
    login_url: t.LoginUrl | None = None
    switch_inline_query: str | None = None
    switch_inline_query_current_chat: str | None = None
    switch_inline_query_chosen_chat: t.SwitchInlineQueryChosenChat | None = None
    copy_text: t.CopyTextButton | None = None
    callback_game: t.CallbackGame | None = None
    pay: bool | None = None

    def __post_init__(self):
        non_action_fields = ["text", "row", "icon_custom_emoji_id", "style"]
        if not any(
            getattr(self, f.name)
            for f in fields(self)
            if f.name not in non_action_fields
        ):
            raise ValueError(
                "At least one required: url, callback data etc. \n"
                "See docs https://docs.aiogram.dev/en/latest/api/types/inline_keyboard_button.html"
            )

        if not self.text:
            raise ValueError("button label required")

        if self.row < 1:
            raise ValueError("row must be greater or equal to 1")

        if len(self.text) > 64:
            raise ValueError("max button label length is 64")

        if self.callback_data and len(self.callback_data) > 64:
            raise ValueError("max callback_data length is 64")


def create_button(dto: InlineButton) -> t.InlineKeyboardButton:
    return t.InlineKeyboardButton(
        text=dto.text,
        icon_custom_emoji_id=dto.icon_custom_emoji_id,
        style=dto.style,
        url=dto.url,
        callback_data=dto.callback_data,
        web_app=dto.web_app,
        login_url=dto.login_url,
        switch_inline_query=dto.switch_inline_query,
        switch_inline_query_current_chat=dto.switch_inline_query_current_chat,
        switch_inline_query_chosen_chat=dto.switch_inline_query_chosen_chat,
        copy_text=dto.copy_text,
        callback_game=dto.callback_game,
        pay=dto.pay,
    )


def create_back_button(path: str) -> t.InlineKeyboardButton:
    return t.InlineKeyboardButton(
        text=BACK_TEXT,
        callback_data=MenuCallback(
            path=".".join(path.split(".")[:-1]) or "root"
        ).pack(),
    )


def has_button(
    keyboard: t.InlineKeyboardMarkup,
    label: str,
) -> bool:
    return any(
        button.text == label for row in keyboard.inline_keyboard for button in row
    )


def inline_kb(buttons: list[InlineButton], **kwargs) -> t.InlineKeyboardMarkup | None:
    if len(buttons) == 0:
        return None
    rows = [[] for _ in range(max([x.row for x in buttons]))]

    for button in buttons:
        rows[button.row - 1].append(create_button(button))

    return t.InlineKeyboardMarkup(
        inline_keyboard=rows,
        **kwargs,
    )


def build_callback(item: MenuItem, menu_path: str) -> str:
    """
    Build callback data for a menu item.
    Args:
        item: Menu item for which the callback is created.
        menu_path: Path to the item without the root id,
            e.g. option_1.sub_option_1.<item_id>.
    """
    match item.type:
        case "menu":
            path = item.id if menu_path == MENU.id else f"{menu_path}.{item.id}"
            return MenuCallback(path=path).pack()
        case "action":
            return AwaitedActionCallback(action=item.id).pack()


def build_keyboard(item: MenuItem, path: str) -> t.InlineKeyboardMarkup | None:
    if not item:
        return None

    keyboard = inline_kb(
        [
            InlineButton(text=c.button_text, callback_data=build_callback(c, path))
            for c in item.children
        ],
    )
    if not keyboard:
        return t.InlineKeyboardMarkup(inline_keyboard=[[create_back_button(path)]])
    if path != MENU.id:
        keyboard.inline_keyboard.append([create_back_button(path)])

    return keyboard
