# -*- coding: utf-8 -*-

class GuardrailException(Exception):
    pass


class RecordNotSaved(GuardrailException):
    pass


class SchemaNotFound(GuardrailException):
    pass


class PermissionExists(GuardrailException):
    pass


class PermissionNotFound(GuardrailException):
    pass
