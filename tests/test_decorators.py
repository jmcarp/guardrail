# -*- coding: utf-8 -*-

import mock
import pytest

from guardrail.core import decorators


class ErrorHandlerException(Exception):
    pass


@pytest.fixture
def manager():
    return mock.Mock()


@pytest.fixture
def agent_loader():
    return mock.Mock()


@pytest.fixture
def target_loader():
    return mock.Mock()


@pytest.fixture
def error_handler():
    def side_effect(code):
        raise ErrorHandlerException(code)
    return mock.Mock(side_effect=side_effect)


@pytest.fixture
def protected(manager, agent_loader, target_loader, error_handler):
    decorator = decorators.has_permission(
        'code',
        manager,
        agent_loader,
        target_loader,
        error_handler,
    )
    @decorator
    def _protected(agent=None, target=None, **kwargs):
        return agent, target, kwargs
    return _protected


def test_has_permission_true(manager, agent_loader, target_loader,
                             error_handler, protected):
    manager.has_permission.return_value = True
    data = {'song': 'somebody to love'}
    agent, target, kwargs = protected(**data)
    agent_loader.assert_called_with(**data)
    target_loader.assert_called_with(**data)
    manager.has_permission.assert_called_with(
        agent_loader.return_value,
        target_loader.return_value,
        'code',
    )
    assert not error_handler.called
    assert agent == agent_loader.return_value
    assert target == target_loader.return_value
    assert kwargs == data


def test_has_permission_agent_not_found(manager, agent_loader, target_loader,
                                        error_handler, protected):
    agent_loader.return_value = None
    with pytest.raises(ErrorHandlerException):
        agent, target, kwargs = protected()
    assert not manager.called
    error_handler.assert_called_with(decorators.AGENT_NOT_FOUND)


def test_has_permission_target_not_found(manager, agent_loader, target_loader,
                                         error_handler, protected):
    target_loader.return_value = None
    with pytest.raises(ErrorHandlerException):
        agent, target, kwargs = protected()
    assert not manager.called
    error_handler.assert_called_with(decorators.TARGET_NOT_FOUND)


def test_has_permission_false(manager, agent_loader, target_loader,
                              error_handler, protected):
    manager.has_permission.return_value = False
    with pytest.raises(ErrorHandlerException):
        agent, target, kwargs = protected()
    error_handler.assert_called_with(decorators.FORBIDDEN)
