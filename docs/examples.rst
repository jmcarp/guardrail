Examples
========

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

