import pytest

from src.application.use_cases.register_user import RegisterUserUseCase
from src.container import Container


@pytest.mark.asyncio
async def test_container(session, settings):
    container = Container(settings)

    uc = container.register_user_use_case(session)
    assert isinstance(uc, RegisterUserUseCase)
