import pytest

from domain.entities.operator import Operator
from infrastructure.database.models import OperatorModel
from infrastructure.database.repositories.operator_repository import OperatorRepository


def test_entity_to_instance(session, operator_entity):
    repository = OperatorRepository(session)
    id_ = 1
    entity = operator_entity(id=id_)

    instance = repository.entity_to_instance(entity)

    assert isinstance(instance, OperatorModel)
    assert instance.id == id_


def test_instance_to_entity(session, operator_instance):
    repository = OperatorRepository(session)
    id_ = 1
    instance = operator_instance(id=id_)

    entity = repository.instance_to_entity(instance)

    assert isinstance(entity, Operator)
    assert entity.id == id_


@pytest.mark.asyncio
async def test_find_by_email(session, operator_entity):
    email = "find_test@test.com"
    repository = OperatorRepository(session)
    id_ = 1
    entity = operator_entity(id=id_, email=email)

    no_operator = await repository.find_by_email(email)

    assert no_operator is None

    await repository.persist(entity)

    operator = await repository.find_by_email(email)

    assert isinstance(operator, Operator)
    assert operator.email == email
