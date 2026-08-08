
import pytest

from src.domain.entities.support_message import SupportMessage
from src.infrastructure.database.models import SupportMessageModel
from src.infrastructure.database.repositories.support_message_repository import (
    SupportMessageRepository,
)


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
async def test_get_and_save_message(session, support_message_entity):
    repository = SupportMessageRepository(session)
    id_ = 1
    entity = support_message_entity(id=id_)

    message = await repository.get_message(id_)
    assert message is None

    message = await repository.persist(entity)
    assert isinstance(message, SupportMessage)
    assert message.id == id_

    message = await repository.get_message(id_)
    assert isinstance(message, SupportMessage)


@pytest.mark.asyncio
async def test_get_messages_by_chat(session, support_message_entity):
    repository = SupportMessageRepository(session)
    chat_id = 2

    messages = await repository.get_messages_by_chat(chat_id)

    assert isinstance(messages, list)
    assert not messages

    messages_amount = 2

    for i in range(messages_amount):
        entity = support_message_entity(id=i)
        await repository.persist(entity)

    messages = await repository.get_messages_by_chat(chat_id)

    assert isinstance(messages, list)
    assert len(messages) == messages_amount
    assert all(m.chat_id == chat_id for m in messages)
