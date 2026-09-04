import os

import pytest
from pydantic import ValidationError

from config import Settings


def test_assemble_rabbitmq_url_from_user_and_password(setup_base_env):
    mock_data = {"RABBITMQ_USER": "admin", "RABBITMQ_PASSWORD": "strong_pass"}

    result = Settings.assemble_rabbitmq_url(mock_data)

    assert result.get("RABBITMQ_URL") == "amqp://admin:strong_pass@localhost:5672/"


def test_rabbitmq_url_not_overwritten_if_already_exists(setup_base_env):
    custom_url = "amqp://cloud-rabbit.com"
    os.environ["RABBITMQ_URL"] = custom_url
    os.environ["RABBITMQ_USER"] = "ignored_user"
    os.environ["RABBITMQ_PASSWORD"] = "ignored_pass"

    settings = Settings(_env_file=None)

    assert settings.rabbitmq_url == custom_url


def test_settings_validation_error_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "db_name" in str(exc_info.value)
