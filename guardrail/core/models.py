# -*- coding: utf-8 -*-

import abc

import six

from guardrail.core import exceptions
from guardrail.core.registry import registry


def _get_class(value):
    return value if isinstance(value, type) else type(value)


@six.add_metaclass(abc.ABCMeta)
class BasePermissionManager(object):

    def __init__(self, registry=registry):
        self.registry = registry

    def get_permissions(self, agent, target):
        schema = self._get_permission_schema(agent, target)
        return self._get_permissions(agent, target, schema)

    def has_permission(self, agent, target, permission):
        schema = self._get_permission_schema(agent, target)
        return self._has_permission(agent, target, schema, permission)

    def add_permission(self, agent, target, permission):
        schema = self._get_permission_schema(agent, target)
        return self._add_permission(agent, target, schema, permission)

    def remove_permission(self, agent, target, permission):
        schema = self._get_permission_schema(agent, target)
        return self._remove_permission(agent, target, schema, permission)

    def _get_permission_schema(self, agent, target):
        self._check_saved(agent, target)
        return self.registry.get_permission(_get_class(agent), _get_class(target))

    def _check_saved(self, *records):
        for record in records:
            if not self._is_saved(record):
                raise exceptions.RecordNotSaved('Record {0!r} not saved'.format(record))

    @abc.abstractmethod
    def _is_saved(self, record):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _get_permissions(self, agent, target, schema):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _has_permission(self, agent, target, schema, permission):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _add_permission(self, agent, target, schema, permission):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _remove_permission(self, agent, target, schema, permission):
        pass  # pragma: no cover


@six.add_metaclass(abc.ABCMeta)
class BasePermissionSchemaFactory(object):

    def __init__(self, bases):
        self.bases = bases

    def __call__(self, agent, target):
        self._update_parents(agent, target)
        return type(
            self._make_schema_name(agent, target),
            self.bases,
            self._make_schema_dict(agent, target),
        )

    def _update_parents(self, agent, target):
        pass

    def _make_schema_name(self, agent, target):
        return '{0}{1}Permission'.format(
            agent.__name__,
            target.__name__,
        )

    def _make_table_name(self, agent, target):
        return '{0}_{1}_permission'.format(
            self._get_table_name(agent),
            self._get_table_name(target),
        )

    @abc.abstractmethod
    def _get_table_name(self, schema):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _make_schema_dict(self, agent, target):
        pass  # pragma: no cover


class BaseLoader(object):

    def __init__(self, schema, column, kwarg='id'):
        self.schema = schema
        self.column = column
        self.kwarg = kwarg

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass  # pragma: no cover
