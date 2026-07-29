from aiogram import Dispatcher

from src.infrastructure.telegram.handlers.start import router as start_router


def register_all_routers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
