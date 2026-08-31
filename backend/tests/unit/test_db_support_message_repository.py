import pytest

from domain.entities.support_message import SupportMessage
from infrastructure.database.models import SupportMessageModel
from infrastructure.database.repositories.support_message_repository import SupportMessageRepository


def test_entity_to_instance(session, support_message_entity):
    repository = SupportMessageRepository(session)
    id_ = 1
    entity = support_message_entity(id=id_)

    instance = repository.entity_to_instance(entity)

    assert isinstance(instance, SupportMessageModel)
    assert instance.id == id_


def test_instance_to_entity(session, support_message_instance):
    repository = SupportMessageRepository(session)
    id_ = 1
    instance = support_message_instance(id=id_)

    entity = repository.instance_to_entity(instance)

    assert isinstance(entity, SupportMessage)
    assert entity.id == id_


@pytest.mark.asyncio
async def test_get_all_by_chat(session, support_message_entity):
    repository = SupportMessageRepository(session)
    chat_id = 2

    messages = await repository.get_all_by_chat_id(chat_id)

    assert isinstance(messages, list)
    assert not messages

    messages_amount = 2

    for i in range(messages_amount):
        entity = support_message_entity(id=i)
        await repository.persist(entity)

    messages = await repository.get_all_by_chat_id(chat_id)

    assert isinstance(messages, list)
    assert len(messages) == messages_amount
    assert all(isinstance(m, SupportMessage) and m.chat_id == chat_id for m in messages)
