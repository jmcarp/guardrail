# -*- coding: utf-8 -*-
"""SQLAlchemy plugin for guardrail."""

from __future__ import absolute_import

import sqlalchemy as sa

from guardrail.core import models
from guardrail.core import exceptions
from guardrail.core.registry import registry


def _get_primary_column(schema):
    primary = sa.inspection.inspect(schema).primary_key
    if len(primary) == 1:
        return primary[0]
    raise RuntimeError('Composite foreign keys not currently supported')


class SqlalchemyPermissionManager(models.BasePermissionManager):

    def __init__(self, session, registry=registry):
        super(SqlalchemyPermissionManager, self).__init__(registry)
        self.session = session

    @staticmethod
    def _is_saved(record):
        return True

    @staticmethod
    def _build_query(query, agent, target, schema, Agent=None, Target=None, custom=None):
        if Agent is None:
            query = query.filter(schema.agent == agent)
        if Target is None:
            query = query.filter(schema.target == target)
        if custom is not None:
            query = custom(query, agent=agent, target=target, schema=schema)
        return query

    def _get_permissions(self, agent, target, schema,
                         Agent=None, Target=None, custom=None):
        query = self.session.query(schema.permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return {each.permission for each in query}

    def _has_permission(self, agent, target, schema, permission,
                        Agent=None, Target=None, custom=None):
        query = self.session.query(schema.permission)
        query = query.filter(schema.permission == permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return bool(query.first())

    def _add_permission(self, agent, target, schema, permission):
        row = schema(
            agent=agent,
            target=target,
            permission=permission,
        )
        self.session.add(row)
        try:
            self.session.flush()
        except sa.exc.IntegrityError:
            self.session.rollback()
            raise exceptions.PermissionExists()
        return row

    def _remove_permission(self, agent, target, schema, permission):
        query = self.session.query(schema)
        query = query.filter(schema.permission == permission)
        query = self._build_query(query, agent, target, schema)
        count = query.delete()
        if not count:
            raise exceptions.PermissionNotFound


def _reference_column(schema, **kwargs):
    return sa.Column(
        sa.Integer,
        sa.ForeignKey(
            _get_primary_column(schema),
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        **kwargs
    )


class SqlalchemyPermissionSchemaFactory(models.BasePermissionSchemaFactory):
    """Permission schema factory for use with SQLAlchemy.

    :param tuple bases: Base classes for created schema classes
    :param bool cascade: Database backend supports `ON DELETE` and `ON UPDATE`
        cascades; see :meth:`_update_parents` for details
    """
    def __init__(self, bases, cascade=False):
        super(SqlalchemyPermissionSchemaFactory, self).__init__(bases)
        self.cascade = cascade

    @staticmethod
    def _get_table_name(schema):
        return schema.__tablename__

    def _update_parents(self, agent, target, schema):
        """Create a many-to-many `relationship` between the `agent` and `target`
        schemas, using the created `schema` as the join table.

        Note: Use the `passive_deletes` and `passive_updates` flags only if the
        database backend supports the ON UPDATE and ON DELETE cascades. These
        options are not supported in SQLite, or in MySQL using the MyISAM storage
        engine.
        """
        attr = 'targets_{0}'.format(schema.__tablename__)
        backref = 'agents_{0}'.format(schema.__tablename__)
        relation = sa.orm.relationship(
            target,
            secondary=schema.__table__,
            backref=backref,
            passive_deletes=self.cascade,
            passive_updates=self.cascade,
        )
        setattr(agent, attr, relation)

    def _make_schema_dict(self, agent, target):
        return dict(
            __tablename__=self._make_table_name(agent, target),
            __table_args__=(
                sa.UniqueConstraint('agent_id', 'target_id', 'permission'),
            ),
            id=sa.Column(sa.Integer, primary_key=True),
            agent_id=_reference_column(agent, nullable=False, index=True),
            agent=sa.orm.relationship(agent),
            target_id=_reference_column(target, nullable=False, index=True),
            target=sa.orm.relationship(target),
            permission=sa.Column(sa.String, nullable=False, index=True),
        )


class SqlalchemyLoader(models.BaseLoader):

    def __init__(self, schema, session, column=None, kwarg='id'):
        column = column if column is not None else _get_primary_column(schema)
        super(SqlalchemyLoader, self).__init__(schema, column, kwarg)
        self.session = session

    def __call__(self, *args, **kwargs):
        return self.session.query(
            self.schema
        ).filter(
            self.column == kwargs.get(self.kwarg)
        ).first()
