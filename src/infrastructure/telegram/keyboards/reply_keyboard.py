from dataclasses import dataclass, fields
from typing import Literal

import aiogram.types as t


@dataclass
class ReplyButton:
    text: str  # label

    row: int = 1
    icon_custom_emoji_id: str | None = None
    style: Literal["danger", "success", "primary"] | None = None  # red, green or blue

    request_users: t.KeyboardButtonRequestUsers | None = None
    request_chat: t.KeyboardButtonRequestChat | None = None
    request_managed_bot: (
        t.keyboard_button_request_managed_bot.KeyboardButtonRequestManagedBot | None
    ) = None
    request_contact: bool | None = None
    request_location: bool | None = None
    request_poll: t.KeyboardButtonPollType | None = None
    web_app: t.WebAppInfo | None = None
    request_user: t.KeyboardButtonRequestUser | None = None

    def __post_init__(self):
        non_action_fields = ["text", "row", "icon_custom_emoji_id", "style"]
        if (
            len(
                [
                    f
                    for f in fields(self)
                    if f.name not in non_action_fields
                    and getattr(self, f.name) is not None
                ]
            )
            > 1
        ):
            raise ValueError(
                "At most one must be used: url, callback data etc. \n"
                "See docs https://docs.aiogram.dev/en/latest/api/types/keyboard_button.html"
            )

        if not self.text:
            raise ValueError("button label required")

        if self.row < 1:
            raise ValueError("row must be greater or equal to 1")

        if len(self.text) > 64:
            raise ValueError("max button label length is 64")


def create_button(dto: ReplyButton) -> t.KeyboardButton:
    return t.KeyboardButton(
        text=dto.text,
        icon_custom_emoji_id=dto.icon_custom_emoji_id,
        style=dto.style,
        request_users=dto.request_users,
        request_chat=dto.request_chat,
        request_managed_bot=dto.request_managed_bot,
        request_contact=dto.request_contact,
        request_location=dto.request_location,
        request_poll=dto.request_poll,
        web_app=dto.web_app,
        request_user=dto.request_user,
    )


def reply_kb(buttons: list[ReplyButton], **kwargs) -> t.ReplyKeyboardMarkup:
    """
    Creates ReplyKeyboardMarkup.
    If there are not consecutive row numbers (ex. 1,2,4), telegram removes the gaps automatically
    Must contain at least one ReplyButton
    """
    if len(buttons) == 0:
        raise ValueError("input contains no buttons")

    rows = [[] for _ in range(max([x.row for x in buttons]))]
    for button in buttons:
        rows[button.row - 1].append(create_button(button))

    return t.ReplyKeyboardMarkup(
        keyboard=rows,
        is_persistent=kwargs.get("is_persistent"),
        resize_keyboard=kwargs.get("resize_keyboard"),
        one_time_keyboard=kwargs.get("one_time_keyboard"),
        input_field_placeholder=kwargs.get("input_field_placeholder"),
        selective=kwargs.get("selective"),
    )
