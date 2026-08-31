import pytest

from container import Container


@pytest.fixture()
def container(settings, session_factory):
    container = Container(settings)
    container.session_factory = session_factory

    return container
