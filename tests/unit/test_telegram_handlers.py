from __future__ import annotations

from unittest.mock import patch

import pytest


from aiogram import Dispatcher, Router

from src.infrastructure.telegram.handlers import register_all_routers


def test_handlers_init():
    fake_router = Router(name="test")
    with patch(
         "src.infrastructure.telegram.handlers.start_router",
         fake_router,
    ):
        dp = Dispatcher()
        assert len(dp.sub_routers) == 0

        register_all_routers(dp)

        routes_name = [x.name for x in dp.sub_routers]

        assert "test" in routes_name
