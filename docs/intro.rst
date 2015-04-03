Intro
=====

**guardrail** is a Python library for managing object-level permissions with
support for arbitrary ORMs and web frameworks. Other libraries like `django-guardian
<https://github.com/lukaszb/django-guardian>`_ handle this problem well for
particular frameworks, but **guardrail** makes it simple to implement object-
level permissions for any framework.

**guardrail** includes a set of abstract base classes for writing framework-
specific plugins, as well as plugins supporting object-level permissions for
SQLAlchemy, Peewee, Pony ORM, and Django ORM. Writing new plugins is fairly
straightforward. Although current plugins are limited to SQL ORMs, adding support
for NoSQL stored would be fairly straightforward as well.
