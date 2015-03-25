# -*- coding: utf-8 -*-

import abc

import six

from guardrail.core import exceptions
from guardrail.core.registry import registry


def _get_class(value):
    return value if isinstance(value, type) else type(value)


@six.add_metaclass(abc.ABCMeta)
class BasePermissionManager(object):
    """Abstract base class for permission managers. Concrete subclasses must
    implement CRUD operations (check, add, and remove permissions), as well as
    the :meth:`is_saved` check.

    :param _Registry registry: Optional registry object; use global `registry`
        if not provided.
    """
    def __init__(self, registry=registry):
        self.registry = registry

    def get_permissions(self, agent, target):
        """List all permissions record `agent` has on record `target`.

        :param agent: Agent record
        :param target: Target record
        :returns: Set of permission labels between `agent` and `target`
        """
        schema = self._get_permission_schema(agent, target)
        return self._get_permissions(agent, target, schema)

    def has_permission(self, agent, target, permission):
        """Check whether record `agent` has permission `permission` on record
        `target`.

        :param agent: Agent record
        :param target: Target record
        :param str permission: Permission
        :returns: Record `agent` has permission `permission` on record `target`
        """
        schema = self._get_permission_schema(agent, target)
        return self._has_permission(agent, target, schema, permission)

    def add_permission(self, agent, target, permission):
        """Grant permission `permission` to record `agent` on record `target`.

        :param agent: Agent record
        :param target: Target record
        :param str permission: Permission
        :returns: Created permission record
        :raises: `PermissionExistsError` if permission has already been granted
        """
        schema = self._get_permission_schema(agent, target)
        return self._add_permission(agent, target, schema, permission)

    def remove_permission(self, agent, target, permission):
        """Revoke permission `permission` from record `agent` on record `target`.

        :param agent: Agent record
        :param target: Target record
        :param str permission: Permission
        :raises: `PermissionNotFound` if permission has not been granted
        """
        schema = self._get_permission_schema(agent, target)
        return self._remove_permission(agent, target, schema, permission)

    def _get_permission_schema(self, agent, target):
        """Look up join table linking `agent` and `target`, verifying that both
        records have been persisted.

        :param agent: Agent record
        :param target: Target record
        :returns: Join table between `agent` and `target`
        :raises: `RecordNotSaved` if either record has not been persisted
        :raises: `SchemaNotFound` if no join table exists
        """
        self._check_saved(agent, target)
        return self.registry.get_permission(_get_class(agent), _get_class(target))

    def _check_saved(self, *records):
        for record in records:
            if not self._is_saved(record):
                raise exceptions.RecordNotSaved('Record {0!r} not saved'.format(record))

    @abc.abstractmethod
    def _is_saved(self, record):
        """Check whether `record` has been persisted. Note: For backends that
        do not require records to be persisted to operate on foreign-key
        relationships, this method should always return `True`.

        :param record: Record to check
        :returns: `record` has been persisted
        """
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
    """Abstract base class for schema factories that create permission join
    tables. Concrete subclasses must implement :meth:`_get_table_name` and
    :meth:`_make_schema_dict`.

    :param tuple bases: Base classes for created schema classes
    """
    def __init__(self, bases):
        self.bases = bases

    def __call__(self, agent, target):
        """Create a join table representing permissions between `agent` and
        `target` schemas.

        :param agent: Agent schema class
        :param target: Target schema class
        :returns: Created schema
        """
        self._update_parents(agent, target)
        return type(
            self._make_schema_name(agent, target),
            self.bases,
            self._make_schema_dict(agent, target),
        )

    def _update_parents(self, agent, target):
        """Creating a permission join table may require mutating the `agent`
        and `target` schemas. By default, take no action.

        :param agent: Agent schema class
        :param target: Target schema class
        """
        pass

    def _make_schema_name(self, agent, target):
        """Build class name for permission join table.

        :param agent: Agent schema class
        :param target: Target schema class
        """
        return '{0}{1}Permission'.format(
            agent.__name__,
            target.__name__,
        )

    def _make_table_name(self, agent, target):
        """Build table name for permission join table.

        :param agent: Agent schema class
        :param target: Target schema class
        """
        return '{0}_{1}_permission'.format(
            self._get_table_name(agent),
            self._get_table_name(target),
        )

    @abc.abstractmethod
    def _get_table_name(self, schema):
        """Get table name for `schema`.

        :param schema: Schema class
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def _make_schema_dict(self, agent, target):
        """Build class dictionary for permission join table.

        :param agent: Agent schema class
        :param target: Target schema class
        :returns: Dictionary of class members
        """
        pass  # pragma: no cover


class BaseLoader(object):

    def __init__(self, schema, column, kwarg='id'):
        self.schema = schema
        self.column = column
        self.kwarg = kwarg

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        pass  # pragma: no cover
