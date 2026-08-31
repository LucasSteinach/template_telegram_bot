from aiogram import Dispatcher

from container import Container
from infrastructure.telegram.middlewares.callback_middlewares import (
    CallbackLockMiddleware,
)
from infrastructure.telegram.middlewares.container_middleware import (
    ContainerMiddleware,
)


def register_middlewares(dp: Dispatcher, container: Container) -> None:
    dp.update.outer_middleware(ContainerMiddleware(container))
    dp.callback_query.outer_middleware(CallbackLockMiddleware())
