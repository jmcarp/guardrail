# -*- coding: utf-8 -*-

from guardrail.core import exceptions


class _Registry(object):

    def __init__(self):
        self._agents = set()
        self._targets = set()
        self._permissions = dict()

    @property
    def agents(self):
        return self._agents

    @property
    def targets(self):
        return self._targets

    @property
    def permissions(self):
        return self._permissions.values()

    def agent(self, agent):
        self._agents.add(agent)
        return agent

    def target(self, target):
        self._targets.add(target)
        return target

    def add_permission(self, agent, target, permission):
        self._permissions[(agent, target)] = permission

    def get_permission(self, agent, target):
        try:
            return self._permissions[(agent, target)]
        except KeyError:
            raise exceptions.SchemaNotFound(
                'Could not find permission schema linking models {0} and {1}'.format(
                    agent.__name__,
                    target.__name__,
                )
            )

    def make_schemas(self, factory):
        for agent in self.agents:
            for target in self.targets:
                permission = factory(agent, target)
                self.add_permission(agent, target, permission)


registry = _Registry()
