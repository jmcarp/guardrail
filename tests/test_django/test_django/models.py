# -*- coding: utf-8 -*-

from django import db

from guardrail.ext.django.models import DjangoPermissionSchemaFactory

from .registry import registry


@registry.agent
class Agent(db.models.Model):
    pass


@registry.target
class Target(db.models.Model):
    pass


factory = DjangoPermissionSchemaFactory((db.models.Model, ))
registry.make_schemas(factory)
