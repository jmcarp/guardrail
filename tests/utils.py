# -*- coding: utf-8 -*-

import six


def patch(obj, **kwargs):
    for key, value in six.iteritems(kwargs):
        setattr(obj, key, value)
