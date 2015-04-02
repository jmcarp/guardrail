# -*- coding: utf-8 -*-
"""Custom object permissions backend for Django plugin"""

from .models import DjangoPermissionManager


class ObjectPermissionBackend(object):
    """Custom authentication backend for object-level permissions. Must be used
    in conjunction with a backend that handles the `authenticate` and `get_user`
    methods, such as the default `django.contrib.auth.backends.ModelBackend`.
    """
    def authenticate(self, username=None, password=None, *kwargs):
        return None

    def get_user(self, user_id):
        return None

    def has_perm(self, user, perm, target=None):
        manager = DjangoPermissionManager()
        return manager.has_permission(user, target, perm)

    def get_all_permissions(self, user, target=None):
        manager = DjangoPermissionManager()
        return manager.get_permissions(user, target)
