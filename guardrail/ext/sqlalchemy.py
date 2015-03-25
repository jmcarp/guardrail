# -*- coding: utf-8 -*-

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
    def _base_query(agent, target, schema):
        return (
            schema.agent_id == agent.id,
            schema.target_id == target.id,
        )

    def _get_permissions(self, agent, target, schema):
        query = self.session.query(
            schema.permission
        ).filter(
            *self._base_query(agent, target, schema)
        )
        return {each.permission for each in query}

    def _has_permission(self, agent, target, schema, permission):
        row = self.session.query(
            schema.permission
        ).filter(
            schema.permission == permission,
            *self._base_query(agent, target, schema)
        ).first()
        return bool(row)

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
        count = self.session.query(
            schema
        ).filter(
            schema.permission == permission,
            *self._base_query(agent, target, schema)
        ).delete()
        if not count:
            raise exceptions.PermissionNotFound


def _reference_column(schema, **kwargs):
    return sa.Column(
        sa.Integer,
        sa.ForeignKey(_get_primary_column(schema)),
        **kwargs
    )


class SqlalchemyPermissionSchemaFactory(models.BasePermissionSchemaFactory):

    @staticmethod
    def _get_table_name(schema):
        return schema.__tablename__

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
        column = column or _get_primary_column(schema)
        super(SqlalchemyLoader, self).__init__(schema, column, kwarg)
        self.session = session

    def __call__(self, *args, **kwargs):
        return self.session.query(
            self.schema
        ).filter(
            self.column == kwargs.get(self.kwarg)
        ).first()
