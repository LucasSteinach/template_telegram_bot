from domain.entities.user import User
from infrastructure.database.models import UserModel
from infrastructure.database.repositories.user_repository import UserRepository


def test_entity_to_instance(session, user_entity):
    repository = UserRepository(session)
    id_ = 1
    entity = user_entity(id=id_)

    instance = repository.entity_to_instance(entity)

    assert isinstance(instance, UserModel)
    assert instance.id == id_


def test_instance_to_entity(session, user_instance):
    repository = UserRepository(session)
    id_ = 1
    instance = user_instance(id=id_)

    entity = repository.instance_to_entity(instance)

    assert isinstance(entity, User)
    assert entity.id == id_
