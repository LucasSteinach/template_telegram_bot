from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers.main_menu import router as main_menu_router
from src.infrastructure.telegram.handlers.start import router as start_router


def get_all_routers() -> list[Router]:
    return [start_router, main_menu_router]


def register_routers(dp: Dispatcher) -> None:
    for r in get_all_routers():
        dp.include_router(r)
