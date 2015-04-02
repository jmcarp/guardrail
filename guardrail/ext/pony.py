# -*- coding: utf-8 -*-
"""Pony plugin for guardrail."""

from __future__ import absolute_import

import pony.orm as pn

from guardrail.core import models
from guardrail.core import exceptions


class PonyPermissionManager(models.BasePermissionManager):

    @staticmethod
    def _is_saved(record):
        return True

    @staticmethod
    def _build_query(query, agent, target, schema,
                     Agent=None, Target=None, custom=None):
        if Agent is None:
            query = query.filter(lambda row: row.agent == agent)
        if Target is None:
            query = query.filter(lambda row: row.target == target)
        if custom is not None:
            query = custom(query, agent=agent, target=target, schema=schema)
        return query

    def _get_permissions(self, agent, target, schema,
                         Agent=None, Target=None, custom=None):
        query = pn.select(row for row in schema)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return {row.permission for row in query}

    def _has_permission(self, agent, target, schema, permission,
                        Agent=None, Target=None, custom=None):
        query = pn.select(row for row in schema if row.permission == permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return query.exists()

    def _add_permission(self, agent, target, schema, permission):
        try:
            return schema(
                agent=agent,
                target=target,
                permission=permission,
            )
        except pn.CacheIndexError:
            raise exceptions.PermissionExists()

    def _remove_permission(self, agent, target, schema, permission):
        query = pn.select(row for row in schema if row.permission == permission)
        query = self._build_query(query, agent, target, schema)
        row = query.first()
        if not row:
            raise exceptions.PermissionNotFound
        row.delete()


class PonyPermissionSchemaFactory(models.BasePermissionSchemaFactory):

    @staticmethod
    def _get_table_name(schema):
        return schema._table_ or schema.__name__

    def _update_schema(self, schema, name, reverse):
        type.__setattr__(schema, name, reverse)
        reverse._init_(schema, name)
        schema._attrs_.append(reverse)
        schema._new_attrs_.append(reverse)

    def _update_agent(self, agent, target, schema):
        reverse = pn.Set(schema)
        name = 'targets_{0}'.format(self._get_table_name(target).lower())
        self._update_schema(agent, name, reverse)

    def _update_target(self, agent, target, schema):
        reverse = pn.Set(schema)
        name = 'agents_{0}'.format(self._get_table_name(agent).lower())
        self._update_schema(target, name, reverse)

    def _update_parents(self, agent, target, schema):
        self._update_agent(agent, target, schema)
        self._update_target(agent, target, schema)

    def _make_schema_dict(self, agent, target):
        return dict(
            _table_=self._make_table_name(agent, target),
            _indexes_=[
                pn.core.Index(
                    'agent', 'target', 'permission',
                    is_pk=False, is_unique=True,
                )
            ],
            id=pn.PrimaryKey(int, auto=True),
            agent=pn.Required(agent, index=True),
            target=pn.Required(target, index=True),
            permission=pn.Required(str, 255, index=True),
        )


class PonyLoader(models.BaseLoader):

    def __init__(self, schema, column=None, kwarg='id'):
        column = column if column is not None else schema._pk_.name
        super(PonyLoader, self).__init__(schema, column, kwarg)

    def __call__(self, *args, **kwargs):
        query = {self.column: kwargs.get(self.kwarg)}
        return pn.select(
            row for row in self.schema
        ).filter(
            **query
        ).first()
