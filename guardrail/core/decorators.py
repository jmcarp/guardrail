# -*- coding: utf-8 -*-

import functools


AGENT_NOT_FOUND = 'agent_not_found'
TARGET_NOT_FOUND = 'target_not_found'
FORBIDDEN = 'forbidden'


class has_permission(object):
    """Factory for permission-checking decorators. Should be subclassed or
    have arguments pre-filled with `functools.partial`.

    :param permission: Permission value
    :param manager: Permission manager
    :param agent_loader: Callable that loads an agent from the `args` and `kwargs`
        passed to the decorated function
    :param target_loader: Callable that loads a target from the `args` and `kwargs`
        passed to the decorated function
    :param error_handler: Callable that handles error codes `AGENT_NOT_FOUND`,
        `TARGET_NOT_FOUND`, and `FORBIDDEN`
    """
    def __init__(self, permission, manager, agent_loader, target_loader, error_handler):
        self.permission = permission
        self.manager = manager
        self.agent_loader = agent_loader
        self.target_loader = target_loader
        self.error_handler = error_handler

    def __call__(self, func):
        """Decorator that checks permissions before calling `func`. Note: wrapped
        function will be called with the loaded agent and target.

        :param func: Callable to decorate
        """
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            agent, target = self._check_permission(*args, **kwargs)
            kwargs.update({
                'agent': agent,
                'target': target,
            })
            return func(*args, **kwargs)
        return wrapped

    def _check_permission(self, *args, **kwargs):
        """Load agent and target records from `agent_loader` and `target_loader`,
        then check for the requested permission. Call `error_handler` if either
        loader returns `None`, or if permission is not present.
        """
        agent = self.agent_loader(*args, **kwargs)
        if not agent:
            return self.error_handler(AGENT_NOT_FOUND)
        target = self.target_loader(*args, **kwargs)
        if not target:
            return self.error_handler(TARGET_NOT_FOUND)
        if not self.manager.has_permission(agent, target, self.permission):
            self.error_handler(FORBIDDEN)
        return agent, target
