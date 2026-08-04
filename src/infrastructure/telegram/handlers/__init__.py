from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers.actions import router as actions_router
from src.infrastructure.telegram.handlers.fallback import router as fallback_router
from src.infrastructure.telegram.handlers.menu import router as menu_router
from src.infrastructure.telegram.handlers.start import router as start_router


def get_all_routers() -> list[Router]:
    return [
        actions_router,
        menu_router,
        start_router,
        fallback_router,  # !always last!
    ]


def register_routers(dp: Dispatcher) -> None:
    for r in get_all_routers():
        dp.include_router(r)
