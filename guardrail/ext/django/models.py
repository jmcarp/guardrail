# -*- coding: utf-8 -*-
"""Note: Define permission schema factory in `models.py` so that Django
migrations detect permission schemas.
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
    def _base_query(agent, target):
        return {
            'agent': agent,
            'target': target,
        }

    def _get_permissions(self, agent, target, schema):
        rows = schema.objects.only(
            'permission',
        ).filter(
            **self._base_query(agent, target)
        )
        return {each.permission for each in rows}

    def _has_permission(self, agent, target, schema, permission):
        return schema.objects.filter(
            permission=permission,
            **self._base_query(agent, target)
        ).exists()

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
        query = schema.objects.filter(
            permission=permission,
            **self._base_query(agent, target)
        )
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
        return self.schema.objects.get(**query)
