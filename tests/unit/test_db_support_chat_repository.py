import pytest

from src.domain.entities.support_chat import ChatStatus, SupportChat
from src.infrastructure.database.models import SupportChatModel
from src.infrastructure.database.repositories.support_chat_repository import (
    SupportChatRepository,
)


def test_entity_to_instance(session, support_chat_entity):
    repository = SupportChatRepository(session)
    id_ = 1
    entity = support_chat_entity(id=id_)

    instance = repository.entity_to_instance(entity)

    assert isinstance(instance, SupportChatModel)
    assert instance.id == id_


def test_instance_to_entity(session, support_chat_instance):
    repository = SupportChatRepository(session)
    id_ = 1
    instance = support_chat_instance(id=id_)

    entity = repository.instance_to_entity(instance)

    assert isinstance(entity, SupportChat)
    assert entity.id == id_


@pytest.mark.asyncio
async def test_get_all_active_chats(session, support_chat_entity):
    repository = SupportChatRepository(session)
    id_ = 1
    entity = support_chat_entity(id=id_, status=ChatStatus.CLOSED)
    await repository.persist(entity)
    active_chat_id = 2
    entity = support_chat_entity(id=active_chat_id)
    await repository.persist(entity)

    chats = await repository.get_all_active_chats()

    assert isinstance(chats, list)
    assert len(chats) == 1
    assert id_ not in [c.id for c in chats]
    assert active_chat_id in [c.id for c in chats]


@pytest.mark.asyncio
async def test_get_all_by_user_id(session, support_chat_entity):
    repository = SupportChatRepository(session)
    user_id = 1
    chats_amount = 2

    for i in range(chats_amount):
        entity = support_chat_entity(id=i, user_id=user_id)
        await repository.persist(entity)

    chats = await repository.get_all_by_user_id(user_id)

    assert isinstance(chats, list)
    assert len(chats) == chats_amount
    assert all(c.user_id == user_id for c in chats)


@pytest.mark.asyncio
async def test_get_all_closed_chats(session, support_chat_entity):
    repository = SupportChatRepository(session)
    id_ = 1
    entity = support_chat_entity(id=id_)
    await repository.persist(entity)
    closed_chat_id = 2
    entity = support_chat_entity(id=closed_chat_id, status=ChatStatus.CLOSED)
    await repository.persist(entity)

    chats = await repository.get_all_closed_chats()

    assert isinstance(chats, list)
    assert len(chats) == 1
    assert id_ not in [c.id for c in chats]
    assert closed_chat_id in [c.id for c in chats]
