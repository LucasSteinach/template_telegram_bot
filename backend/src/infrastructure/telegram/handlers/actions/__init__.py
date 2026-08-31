from aiogram import Router

from src.infrastructure.telegram.handlers.actions.input_data import (
    router as input_data_router,
)
from src.infrastructure.telegram.handlers.actions.support import (
    router as support_router,
)

router = Router(name="actions")

router.include_router(input_data_router)
router.include_router(support_router)
