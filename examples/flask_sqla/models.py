# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

from guardrail.core import registry
from guardrail.ext.sqlalchemy import SqlalchemyPermissionSchemaFactory

db = SQLAlchemy()

@registry.agent
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)

@registry.target
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.Text)

factory = SqlalchemyPermissionSchemaFactory((db.Model, ))
registry.make_schemas(factory)
