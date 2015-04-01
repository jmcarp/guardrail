# -*- coding: utf-8 -*-

import pytest

from tests.utils import patch
from tests.loaders import LoaderMixin
from tests.integration import PermissionManagerMixin

import pony.orm as pn

from guardrail.core.registry import _Registry

from guardrail.ext.pony import PonyLoader
from guardrail.ext.pony import PonyPermissionManager
from guardrail.ext.pony import PonyPermissionSchemaFactory


registry = _Registry()


@pytest.fixture(scope='session')
def database():
    return pn.Database('sqlite', ':memory:')


@pytest.fixture(scope='session')
def Agent(database):
    @registry.agent
    class Agent(database.Entity):
        id = pn.PrimaryKey(int, auto=True)
        name = pn.Optional(str)
    return Agent


@pytest.fixture(scope='session')
def Target(database):
    @registry.target
    class Target(database.Entity):
        id = pn.PrimaryKey(int, auto=True)
        name = pn.Optional(str)
    return Target


@pytest.fixture(scope='session')
def permissions(database):
    factory = PonyPermissionSchemaFactory((database.Entity, ))
    registry.make_schemas(factory)
    database.generate_mapping(create_tables=True)


@pytest.yield_fixture
def transaction(Agent, Target):
    with pn.db_session:
        yield
        pn.rollback()


@pytest.fixture
def integration(request, Agent, Target, permissions, transaction):
    patch(
        request.cls,
        agent=Agent(),
        target=Target(),
        manager=PonyPermissionManager(registry=registry),
    )


@pytest.mark.usefixtures('integration')
class TestPonyPermissionManager(PermissionManagerMixin):

    def delete(self, record):
        record.delete()
        pn.commit()

    def count(self, schema):
        return pn.count(each for each in schema)


@pytest.fixture
def loaders(request, Agent, transaction):
    record = Agent()
    pn.flush()
    patch(
        request.cls,
        Loader=PonyLoader,
        Schema=Agent,
        record=record,
        primary=Agent.id.name,
        secondary=Agent.name.name,
    )


@pytest.mark.usefixtures('loaders')
class TestPonyLoader(LoaderMixin):
    pass
