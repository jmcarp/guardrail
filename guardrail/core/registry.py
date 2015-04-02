# -*- coding: utf-8 -*-

from guardrail.core import exceptions


class _Registry(object):
    """Registry of schemas designated as permission agents and targets, as well
    as the permission tables linking each agent-target pair. Should be used as
    a singleton in ordinary use, but can be instantiated for use in tests.
    """
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
        """Decorator that registers the decorated schema as a permission agent.

        Example:

        .. code-block:: python

            @registry.agent
            class User(Base):
                id = sa.Column(sa.Integer, primary_key=True)

        """
        self._agents.add(agent)
        return agent

    def target(self, target):
        """Decorator that registers the decorated schema as a permission target.

        Example:

        .. code-block:: python

            @registry.target
            class Post(Base):
                id = sa.Column(sa.Integer, primary_key=True)

        """
        self._targets.add(target)
        return target

    def add_permission(self, agent, target, permission):
        """Get the join table linking schemas `agent` and `target`.

        :param agent: Agent schema class
        :param target: Target schema class
        :param schema: Permission join table
        """
        self._permissions[(agent, target)] = permission

    def get_permission(self, agent, target):
        """Get the join table linking schemas `agent` and `target`.

        :param agent: Agent schema class
        :param target: Target schema class
        :returns: Permission join table
        :raises: guardian.core.exceptions.SchemaNotFound if join table does not
            exist
        """
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
        """Create and register join tables linking all registered agent-target
        pairs.

        :param factory: Callable that takes agent and target schemas and returns
            the schema for a permission join table
        """
        for agent in self.agents:
            for target in self.targets:
                permission = factory(agent, target)
                self.add_permission(agent, target, permission)


registry = _Registry()
