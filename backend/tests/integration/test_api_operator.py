from unittest.mock import AsyncMock

import pytest

from application.usecases.support_chat_use_case import SupportChatReadModel
from application.usecases.user_use_case import UserReadModel
from config import ROUTE
from dependencies.usecases import get_support_message_use_case

PATH = "api.operator"


async def login(async_client):
    return await async_client.post(
        ROUTE.LOGIN, json={"email": "test@test.com", "password": "12345678"}
    )


@pytest.mark.asyncio
async def test_get_profile(async_client, app, create_test_operator, create_test_user):
    response = await async_client.get(ROUTE.OPERATOR + "/profile")

    assert response.status_code == 401

    access_token = (await login(async_client)).json()["access_token"]

    response = await async_client.get(
        ROUTE.OPERATOR + "/profile", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert all(field in response.json() for field in UserReadModel.model_fields)


@pytest.mark.parametrize(
    ("route", "response_field", "expected_result"),
    [
        ("/chats/assigned", "operator_id", 12341234),
        ("/chats/waiting", "status", "waiting"),
    ],
    ids=["assigned_chats", "waiting_chats"],
)
@pytest.mark.asyncio
async def test_get_chats(
    async_client,
    app,
    create_test_operator,
    create_test_user,
    create_support_chat,
    route,
    response_field,
    expected_result,
):
    access_token = (await login(async_client)).json()["access_token"]

    response = await async_client.get(
        ROUTE.OPERATOR + route, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert all(item.get(response_field) == expected_result for item in response.json())


@pytest.mark.asyncio
async def test_get_chat(
    async_client, app, create_test_operator, create_test_user, create_support_chat
):
    access_token = (await login(async_client)).json()["access_token"]

    response = await async_client.get(
        ROUTE.OPERATOR + "/chats/1", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert all(field in response.json() for field in SupportChatReadModel.model_fields)


@pytest.mark.asyncio
async def test_send_answer(
    async_client,
    app,
    create_test_operator,
    create_test_user,
    create_support_chat,
    support_message_entity,
):
    access_token = (await login(async_client)).json()["access_token"]

    messages_uc = AsyncMock()
    messages_uc.save_message.return_value = support_message_entity(id=1)

    app.dependency_overrides[get_support_message_use_case] = lambda: messages_uc
    rabbitmq_instance = app.state.container.rabbitmq
    rabbitmq_instance.publish = AsyncMock()

    response = await async_client.post(
        ROUTE.OPERATOR + "/chats/1",
        json={"text": "test_text"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    rabbitmq_instance.publish.assert_awaited_once()
    assert response.status_code == 200
    assert all(field in ["detail", "id"] for field in response.json())
    assert response.json()["id"] == 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_chat_history(
    async_client,
    app,
    create_test_operator,
    create_test_user,
    create_support_chat,
    create_support_message,
):
    access_token = (await login(async_client)).json()["access_token"]

    response = await async_client.get(
        ROUTE.OPERATOR + "/chats/1/history",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert all(field in response.json() for field in ["chat_id", "messages"])
    assert isinstance(response.json()["messages"], list)
    assert len(response.json()["messages"]) == 1
