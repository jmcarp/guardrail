# -*- coding: utf-8 -*-
"""Peewee plugin for guardrail."""

from __future__ import absolute_import

import peewee as pw

from guardrail.core import models
from guardrail.core import exceptions


class PeeweePermissionManager(models.BasePermissionManager):

    @staticmethod
    def _is_saved(record):
        """Peewee cannot create references to unsaved records."""
        return record.get_id() is not None

    @staticmethod
    def _build_query(query, agent, target, schema, Agent=None, Target=None, custom=None):
        if Agent is None:
            query = query.where(schema.agent == agent)
        if Target is None:
            query = query.where(schema.target == target)
        if custom is not None:
            query = custom(query, agent=agent, target=target, schema=schema)
        return query

    def _get_permissions(self, agent, target, schema,
                         Agent=None, Target=None, custom=None):
        query = schema.select(schema.permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return {each.permission for each in query}

    def _has_permission(self, agent, target, schema, permission,
                        Agent=None, Target=None, custom=None):
        query = schema.select(schema.permission)
        query = query.where(schema.permission == permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return bool(query.first())

    def _add_permission(self, agent, target, schema, permission):
        try:
            return schema.create(
                agent=agent,
                target=target,
                permission=permission,
            )
        except pw.IntegrityError:
            raise exceptions.PermissionExists()

    def _remove_permission(self, agent, target, schema, permission):
        query = schema.delete()
        query = query.where(schema.permission == permission)
        query = self._build_query(query, agent, target, schema)
        count = query.execute()
        if not count:
            raise exceptions.PermissionNotFound


def _reference_column(schema, **kwargs):
    return pw.ForeignKeyField(
        schema,
        on_update='CASCADE',
        on_delete='CASCADE',
        **kwargs
    )


class PeeweePermissionSchemaFactory(models.BasePermissionSchemaFactory):
    """Permission schema factory for use with Peewee.

    Note: Peewee does not implement delete and update cascades outside the
    database backend, so care should be taken with deleting agent and target
    records when using a backend that does not support cascades (e.g. SQLite,
    MySQL using the MyISAM storage engine). In this case, use the `recursive`
    flag when deleting through Peewee:

    .. code-block:: python

        agent.delete_instance(recursive=True)

    """
    @staticmethod
    def _get_table_name(schema):
        return schema._meta.db_table

    def _make_schema_meta(self, agent, target):
        return type(
            'Meta',
            (object, ),
            dict(
                db_table=self._make_table_name(agent, target),
                indexes=(
                    (('agent', 'target', 'permission'), True),
                ),
            ),
        )

    def _make_schema_dict(self, agent, target):
        return dict(
            Meta=self._make_schema_meta(agent, target),
            id=pw.PrimaryKeyField(),
            agent=_reference_column(agent, null=False, index=True),
            target=_reference_column(target, null=False, index=True),
            permission=pw.CharField(null=False, index=True),
        )


class PeeweeLoader(models.BaseLoader):

    def __init__(self, schema, column=None, kwarg='id'):
        column = column if column is not None else schema._meta.primary_key
        super(PeeweeLoader, self).__init__(schema, column, kwarg)

    def __call__(self, *args, **kwargs):
        return self.schema.select().where(
            self.column == kwargs.get(self.kwarg)
        ).first()
