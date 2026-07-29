import pytest

from unittest.mock import MagicMock

from src.container import Container
from src.application.use_cases.register_user import RegisterUserUseCase


@pytest.mark.asyncio
async def test_container(session):
    container = Container(session_factory=MagicMock())

    uc = container.register_user_use_case(session)
    assert isinstance(uc, RegisterUserUseCase)
