import pytest
from httpx import ASGITransport, AsyncClient

from api_main import app as fastapi_app


@pytest.fixture
def app(container):
    fastapi_app.state.container = container

    yield fastapi_app


@pytest.fixture
async def async_client(app) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
