import pytest

from src.container import Container


@pytest.fixture()
def container(settings):
    return Container(settings)
