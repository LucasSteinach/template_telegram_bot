import os

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from application.services.auth import create_tokens
from config import Settings


@pytest.fixture(
    # autouse=True  to check for warnings' source
)
def check_gc():
    import tracemalloc

    tracemalloc.start(10)
    yield
    import gc

    gc.collect()


@pytest.fixture
def settings():
    return Settings(
        bot_token="123:test",
        db_user="db_user",
        db_password="db_password",
        db_host="db_host",
        db_port="1234",
        db_name="db_name",
        log_level="DEBUG",
        support_user="12345:@test_support_user",
        fsm_storage="redis",
        redis_url="redis://localhost:6379",
        jwt_secret="secret" * 6,
        access_exp_sec=100,
        refresh_exp_sec=500,
    )


@pytest.fixture(scope="function")
def setup_base_env():
    base_vars = {
        "bot_token": "123:test",
        "db_user": "db_user",
        "db_password": "db_password",
        "db_host": "db_host",
        "db_port": "1234",
        "db_name": "db_name",
        "log_level": "DEBUG",
        "support_user": "12345:@test_support_user",
        "fsm_storage": "redis",
        "redis_url": "redis://localhost:6379",
        "jwt_secret": "",
        "access_exp_sec": "100",
        "refresh_exp_sec": "500",
    }

    for key, value in base_vars.items():
        os.environ[key.upper()] = value

    yield

    for key in base_vars:
        os.environ.pop(key.upper(), None)
    os.environ.pop("RABBITMQ_USER", None)
    os.environ.pop("RABBITMQ_PASSWORD", None)
    os.environ.pop("RABBITMQ_URL", None)


@pytest.fixture
def fake_jwt_credentials():
    def create(**kwargs):
        data = {
            "id_": "1",
            "data": {"role": "operator"},
            "secret": "secret" * 6,
            "access_exp_sec": 10,
            "refresh_exp_sec": 20,
        }
        if kwargs.get("role"):
            role = kwargs.pop("role")
            data["data"]["role"] = role
        data.update(kwargs)
        credentials, _, _ = create_tokens(**data)
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=credentials)

    return create
