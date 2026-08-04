from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class ActionId(StrEnum):
    INPUT_EXAMPLE = "input_example"


class AwaitedActionCallback(CallbackData, prefix="action"):
    action: str


class MenuCallback(CallbackData, prefix="menu"):
    path: str
