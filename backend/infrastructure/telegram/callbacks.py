from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class ActionId(StrEnum):
    INPUT_EXAMPLE = "input_example"
    CHAT = "chat"
    CLOSE_CHAT = "close_chat"


class AwaitedActionCallback(CallbackData, prefix="action"):
    action: str


class MenuCallback(CallbackData, prefix="menu"):
    item_id: str
