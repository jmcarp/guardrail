# -*- coding: utf-8 -*-

import pytest

from tests.utils import patch
from tests.integration import PermissionManagerMixin

import peewee as pw

from guardrail.core.registry import _Registry

from guardrail.ext.peewee import PeeweePermissionManager
from guardrail.ext.peewee import PeeweePermissionSchemaFactory


registry = _Registry()


@pytest.fixture(scope='session')
def db():
    return pw.SqliteDatabase(':memory:', autocommit=False)


@pytest.fixture(scope='session')
def Base(db):
    class Base(pw.Model):
        class Meta:
            database = db
    return Base


@pytest.fixture(scope='session')
def Agent(Base):
    @registry.agent
    class Agent(Base):
        id = pw.PrimaryKeyField()
        name = pw.CharField()
    return Agent


@pytest.fixture(scope='session')
def Target(Base):
    @registry.target
    class Target(Base):
        id = pw.PrimaryKeyField()
        name = pw.CharField()
    return Target


@pytest.fixture(scope='session')
def permissions(db, Base, Agent, Target):
    factory = PeeweePermissionSchemaFactory((Base, ))
    registry.make_schemas(factory)
    db.create_tables([Agent, Target], safe=True)
    db.create_tables(registry.permissions, safe=True)


@pytest.yield_fixture
def transaction(db, Agent, Target, permissions):
    with db.atomic() as transaction:
        yield
        transaction.rollback()


@pytest.fixture
def integration(request, Agent, Target, permissions, transaction):
    patch(
        request.cls,
        agent=Agent.create(name='agent'),
        target=Target.create(name='target'),
        manager=PeeweePermissionManager(registry=registry),
    )


@pytest.mark.usefixtures('integration')
class TestPeeweePermissionManager(PermissionManagerMixin):

    def delete(self, record):
        record.delete_instance(recursive=True)

    def count(self, schema):
        return schema.select().count()
