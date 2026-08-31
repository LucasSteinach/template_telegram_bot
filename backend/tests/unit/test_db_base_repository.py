import pytest

from domain.entities.user import User
from infrastructure.database.repositories.base_repository import (
    FindAllResult,
)
from infrastructure.database.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_find_by_id_empty_db(session):
    repository = UserRepository(session)
    user_id = 1

    user = await repository.find_by_id(user_id)

    assert user is None


@pytest.mark.asyncio
async def test_persist(session, user_entity):
    repository = UserRepository(session)
    user_id = 1
    user: User = user_entity(id=user_id)

    user = await repository.persist(user)

    assert isinstance(user, User)
    assert user.id == user_id

    user = await repository.find_by_id(user_id)

    assert isinstance(user, User)
    assert user.id == user_id


@pytest.mark.asyncio
async def test_delete(session, user_entity):
    repository = UserRepository(session)
    user_id = 1
    user: User = user_entity(id=user_id)
    user = await repository.persist(user)

    assert isinstance(user, User)

    await repository.delete(user_id)
    user = await repository.find_by_id(user_id)

    assert user is None


@pytest.mark.asyncio
async def test_find_by_ids(session, user_entity):
    repository = UserRepository(session)
    for i in range(3):
        entity = user_entity(id=i)
        await repository.persist(entity)

    entities = await repository.find_by_ids([])

    assert entities == []

    ids = [1, 2]
    entities = await repository.find_by_ids(ids)

    assert len(ids) == len(entities)
    assert all(isinstance(e, User) for e in entities)
    assert all(e.id in ids for e in entities)


@pytest.mark.asyncio
async def test_find_all(session, user_entity):
    repository = UserRepository(session)
    entity_count = 3
    roles = ["user", "user", "operator"]
    for i, role in enumerate(roles):
        entity = user_entity(id=i, role=role)
        await repository.persist(entity)

    # clean request
    result = await repository.find_all()

    assert isinstance(result, FindAllResult)
    assert len(result.items) == entity_count
    assert result.total is None

    # where
    result = await repository.find_all(where=[repository._instance.role == "operator"])

    assert len(result.items) == 1
    assert result.items[0].role == "operator"

    # order by
    result = await repository.find_all(
        order_by=[repository._instance.created_at.desc()]
    )

    assert [item.id for item in result.items] == [2, 1, 0]

    # limit offset
    limit, offset = 2, 1
    result = await repository.find_all(
        order_by=[repository._instance.created_at.asc()],
        limit=limit,
        offset=offset,
    )

    assert len(result.items) == limit
    assert [item.id for item in result.items] == [1, 2]

    # include total
    result = await repository.find_all(include_total=True)

    assert result.total == entity_count
