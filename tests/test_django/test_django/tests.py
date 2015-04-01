# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pytest

from tests.utils import patch
from tests.integration import PermissionManagerMixin

from guardrail.ext.django.models import DjangoPermissionManager

from . import models
from .registry import registry


@pytest.fixture
def integration(request):
    patch(
        request.cls,
        agent=models.Agent.objects.create(),
        target=models.Target.objects.create(),
        manager=DjangoPermissionManager(registry=registry),
    )


@pytest.mark.django_db
@pytest.mark.usefixtures('integration')
class TestDjangoPermissionManager(PermissionManagerMixin):

    def delete(self, record):
        record.delete()

    def count(self, schema):
        return schema.objects.count()
