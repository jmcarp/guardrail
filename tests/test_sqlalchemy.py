# -*- coding: utf-8 -*-

import pytest

import functools

from tests.utils import patch
from tests.loaders import LoaderMixin
from tests.integration import PermissionManagerMixin

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from guardrail.core.registry import _Registry

from guardrail.ext.sqlalchemy import SqlalchemyLoader
from guardrail.ext.sqlalchemy import SqlalchemyPermissionManager
from guardrail.ext.sqlalchemy import SqlalchemyPermissionSchemaFactory


registry = _Registry()


Base = declarative_base()


@registry.agent
class Agent(Base):
    __tablename__ = 'agent'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


@registry.target
class Target(Base):
    __tablename__ = 'target'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


@pytest.fixture(scope='session')
def engine():
    return sa.create_engine('sqlite://')


@pytest.fixture(scope='session')
def database(engine):
    factory = SqlalchemyPermissionSchemaFactory((Base, ))
    registry.make_schemas(factory)
    Base.metadata.create_all(engine)


@pytest.yield_fixture
def session(engine, database):
    session_factory = sa.orm.sessionmaker(bind=engine)
    session = sa.orm.scoped_session(session_factory)
    connection = engine.connect()
    with connection.begin() as transaction:
        yield session
        transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def integration(request, session):
    patch(
        request.cls,
        agent=Agent(),
        target=Target(),
        session=session,
        manager=SqlalchemyPermissionManager(session, registry=registry),
    )


@pytest.mark.usefixtures('integration')
class TestSqlalchemyPermissionManager(PermissionManagerMixin):

    def delete(self, record):
        self.session.delete(record)
        self.session.commit()

    def count(self, schema):
        return self.session.query(schema).count()


@pytest.fixture
def loaders(request, session):
    record = Agent()
    session.add(record)
    session.flush()
    patch(
        request.cls,
        session=session,
        Loader=functools.partial(SqlalchemyLoader, session=session),
        Schema=Agent,
        record=record,
        primary=Agent.__table__.c.id,
        secondary=Agent.__table__.c.name,
    )

@pytest.mark.usefixtures('loaders')
class TestSqlalchemyLoader(LoaderMixin):
    pass
