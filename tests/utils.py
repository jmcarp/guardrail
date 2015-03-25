# -*- coding: utf-8 -*-

def patch(obj, **kwargs):
    for key, value in kwargs.iteritems():
        setattr(obj, key, value)
