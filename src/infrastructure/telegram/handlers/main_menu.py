from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.container import Container

router = Router(name="main_menu")


@router.callback_query(F.data == "option_1")
async def handle_option_1(callback: CallbackQuery, container: Container) -> None:
    await callback.answer("option 1")
    await callback.message.edit_text(text="option 1 menu", reply_markup=None)


@router.callback_query(F.data == "option_2")
async def handle_option_2(callback: CallbackQuery, container: Container) -> None:
    await callback.answer("option 2")
    await callback.message.edit_text(text="option 2 menu", reply_markup=None)
