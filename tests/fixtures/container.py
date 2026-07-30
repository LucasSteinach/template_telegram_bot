import pytest

from src.container import Container


@pytest.fixture()
def container(session_factory):
    return Container(session_factory=session_factory)
