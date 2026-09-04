import pytest

from container import Container


@pytest.fixture()
def container(settings, session_factory, redis_storage):
    container = Container(settings)
    container.session_factory = session_factory
    container.redis_storage = redis_storage

    return container
