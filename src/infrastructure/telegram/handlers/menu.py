from aiogram import Router
from aiogram.types import CallbackQuery

from src.infrastructure.telegram.keyboards.inline_keyboard import (
    MenuCallback,
)
from src.infrastructure.telegram.keyboards.menu import render_menu

router = Router(name="menu")


@router.callback_query(MenuCallback.filter())
async def menu_handler(
    callback: CallbackQuery,
    callback_data: MenuCallback,
):
    await callback.answer()
    await render_menu(
        callback.message,
        callback_data.path,
    )
