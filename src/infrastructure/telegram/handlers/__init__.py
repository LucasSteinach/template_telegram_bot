from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers.menu import router as menu_router
from src.infrastructure.telegram.handlers.start import router as start_router


def get_all_routers() -> list[Router]:
    return [start_router, menu_router]


def register_routers(dp: Dispatcher) -> None:
    for r in get_all_routers():
        dp.include_router(r)
