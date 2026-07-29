from dataclasses import dataclass, fields
from typing import Optional, Literal

import aiogram.types as t


@dataclass
class InlineButton:
    text: str  # label

    row: int = 1

    icon_custom_emoji_id: str | None = None
    style: Optional[Literal["danger", "success", "primary"]] = (
        None  # red, green or blue
    )

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
            [
                getattr(self, f.name)
                for f in fields(self)
                if f.name not in non_action_fields
            ]
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


def inline_kb(buttons: list[InlineButton], **kwargs) -> t.InlineKeyboardMarkup:
    """
    Creates InlineKeyboardMarkup.
    If there are not consecutive row numbers (ex. 1,2,4), telegram removes the gaps automatically
    Must contain at least one InlineButton
    """
    if len(buttons) == 0:
        raise ValueError("input contains no buttons")
    rows = [list() for _ in range(max(list(map(lambda x: x.row, buttons))))]

    for button in buttons:
        rows[button.row - 1].append(create_button(button))

    return t.InlineKeyboardMarkup(
        inline_keyboard=rows,
        **kwargs,
    )
