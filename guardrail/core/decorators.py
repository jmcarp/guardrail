# -*- coding: utf-8 -*-

import functools


AGENT_NOT_FOUND = 'agent_not_found'
TARGET_NOT_FOUND = 'target_not_found'
FORBIDDEN = 'forbidden'


class has_permission(object):

    def __init__(self, manager, permission, agent_loader, target_loader, error_handler):
        self.manager = manager
        self.permission = permission
        self.agent_loader = agent_loader
        self.target_loader = target_loader
        self.error_handler = error_handler

    def __call__(self, func):
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
        agent = self.agent_loader(*args, **kwargs)
        if not agent:
            return self.error_handler(AGENT_NOT_FOUND)
        target = self.target_loader(*args, **kwargs)
        if not target:
            return self.error_handler(TARGET_NOT_FOUND)
        if not self.manager.has_permission(agent, target, self.permission):
            self.error_handler(FORBIDDEN)
