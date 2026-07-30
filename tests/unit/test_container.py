from unittest.mock import MagicMock

import pytest

from src.application.use_cases.register_user import RegisterUserUseCase
from src.container import Container


@pytest.mark.asyncio
async def test_container(session):
    container = Container(session_factory=MagicMock())

    uc = container.register_user_use_case(session)
    assert isinstance(uc, RegisterUserUseCase)
