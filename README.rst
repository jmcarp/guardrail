=========
guardrail
=========

.. image:: https://badge.fury.io/py/guardrail.png
    :target: http://badge.fury.io/py/guardrail
    :alt: Latest version

.. image:: https://travis-ci.org/jmcarp/guardrail.png
    :target: https://travis-ci.org/jmcarp/guardrail
    :alt: Travis CI

guardrail is a Python library for managing object-level permissions that's
designed to integrate with arbitrary databases and web frameworks. guardrail
is inspired by `django-guardian <https://github.com/lukaszb/django-guardian>`_
and currently supports the SQLAlchemy, Peewee, Pony, and Django ORMs.

guardrail is easy to integrate with any Python web framework. Documentation and
usage examples coming soon.

Install
-------

::

    pip install guardrail

guardrail supports Python >= 2.7 or >= 3.3 and pypy.


Examples
--------

Define your models as usual, using the `registry.agent` and `registry.target`
decorators to set up permissions relationships:

.. code-block:: python

    import peewee as pw

    from guardrail.core import registry
    from guardrail.ext.peewee import PeeweePermissionSchemaFactory

    database = pw.SqliteDatabase(':memory:')
    class Base(pw.Model):
        class Meta:
            database = database

    @registry.agent
    class User(Base):
        name = pw.CharField()

    @registry.target
    class Post(Base):
        name = pw.CharField()

    @registry.target
    class Comment(Base):
        name = pw.CharField()

    factory = PeeweePermissionSchemaFactory((Base, ))
    registry.make_schemas(factory)

    database.connect()
    database.create_tables([User, Post, Comment], safe=True)
    database.create_tables(registry.permissions, safe=True)

Then use the permission manager to perform CRUD operations on permissions
between any `agent` and `target` models:

.. code-block:: python

    from guardrail.ext.peewee import PeeweePermissionManager

    manager = PeeweePermissionManager()

    user = User.create(name='fred')
    post = Post.create(name='news of the world')
    comment = Comment.create(name='dragon attack')

    manager.add_permission(user, post, 'edit')
    manager.add_permission(user, comment, 'delete')

    manager.has_permission(user, post, 'edit')          # True

    manager.remove_permission(user, comment, 'delete')

    manager.has_permission(user, comment, 'delete')     # False



Project Links
-------------

- PyPI: https://pypi.python.org/pypi/guardrail
- Issues: https://github.com/jmcarp/guardrail/issues


License
-------

MIT licensed. See the `LICENSE <https://github.com/jmcarp/guardrail/blob/master/LICENSE>`_
file for details.
