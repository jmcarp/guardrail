# -*- coding: utf-8 -*-
"""Django plugin for guardrail.
Note: Define permission schema factory in `models.py` so that Django migrations
can detect permission schemas.
"""

from __future__ import absolute_import

from django import db

from guardrail.core import models
from guardrail.core import exceptions


class DjangoPermissionManager(models.BasePermissionManager):

    @staticmethod
    def _is_saved(record):
        """Django cannot create references to unsaved records."""
        return record.pk is not None

    @staticmethod
    def _build_query(query, agent, target, schema,
                     Agent=None, Target=None, custom=None):
        if Agent is None:
            query = query.filter(agent=agent)
        if Target is None:
            query = query.filter(target=target)
        if custom is not None:
            query = custom(query, agent=agent, target=target, schema=schema)
        return query

    def _get_permissions(self, agent, target, schema,
                         Agent=None, Target=None, custom=None):
        query = schema.objects.only('permission')
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return {each.permission for each in query}

    def _has_permission(self, agent, target, schema, permission,
                        Agent=None, Target=None, custom=None):
        query = schema.objects.only('permission')
        query = query.filter(permission=permission)
        query = self._build_query(
            query, agent, target, schema,
            Agent=Agent, Target=Target, custom=custom,
        )
        return query.exists()

    def _add_permission(self, agent, target, schema, permission):
        try:
            return schema.objects.create(
                agent=agent,
                target=target,
                permission=permission,
            )
        except db.IntegrityError:
            raise exceptions.PermissionExists()

    def _remove_permission(self, agent, target, schema, permission):
        query = schema.objects.only('permission')
        query = query.filter(permission=permission)
        query = self._build_query(query, agent, target, schema)
        # Note: This emits an unnecessary extra query. This can be fixed once
        # patch once ticket 16891 is resolved.
        if not query.count():
            raise exceptions.PermissionNotFound
        query.delete()


class DjangoPermissionSchemaFactory(models.BasePermissionSchemaFactory):

    @staticmethod
    def _get_table_name(schema):
        return schema._meta.db_table

    def _make_schema_meta(self, agent, target):
        return type(
            'Meta',
            (object, ),
            dict(
                db_table=self._make_table_name(agent, target),
                unique_together=(('agent', 'target', 'permission'), )
            ),
        )

    def _make_schema_dict(self, agent, target):
        return dict(
            Meta=self._make_schema_meta(agent, target),
            __module__=__name__,
            id=db.models.AutoField(primary_key=True),
            agent=db.models.ForeignKey(agent, null=False, db_index=True),
            target=db.models.ForeignKey(target, null=False, db_index=True),
            permission=db.models.CharField(max_length=255, null=False, db_index=True),
        )


class DjangoLoader(models.BaseLoader):

    def __init__(self, schema, column='pk', kwarg='id'):
        super(DjangoLoader, self).__init__(schema, column, kwarg)

    def __call__(self, *args, **kwargs):
        query = {self.column: kwargs.get(self.kwarg)}
        return self.schema.objects.filter(**query).first()
