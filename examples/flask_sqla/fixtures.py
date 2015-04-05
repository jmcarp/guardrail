# -*- coding: utf-8 -*-

import models
import permissions


def ensure(app):
    with app.app_context():
        user = models.db.session.query(models.User).get(1)
        if not user:
            user = models.User(id=1, username='freddie')
            models.db.session.add(user)
            models.db.session.commit()
        post = models.db.session.query(models.Post).get(1)
        if not post:
            post = models.Post(id=1, title='death on two legs', content='dedicated to...')
            models.db.session.add(post)
            models.db.session.commit()
        try:
            permissions.manager.ensure_permission(user, post, 'read')
        except:
            pass
        models.db.session.commit()
