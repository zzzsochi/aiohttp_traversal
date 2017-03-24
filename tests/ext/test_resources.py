from unittest.mock import Mock, MagicMock
import asyncio

import pytest

from aiohttp_traversal.traversal import Traverser
from aiohttp_traversal.ext.resources import (
    Resource,
    InitCoroMixin,
    Root,
    add_child,
)


def test_Resource_init():  # noqa
    parent = Mock(name='parent', __parent__=None)
    app = MagicMock(name='app')
    app.router.resources = {}
    parent.request.app = parent.app = app
    name = 'name'

    res = Resource(parent, name)

    assert res.__parent__ is parent
    assert res.name == name
    assert res.app is parent.request.app
    assert res.setup is res.app.router.resources.get(Resource)


def test_Resource_init__root():  # noqa
    name = 'root'

    res = Resource(None, name)

    assert res.__parent__ is None
    assert res.name == name
    assert res.app is None
    assert res.setup is None


@pytest.fixture
def res_simple():
    parent = Mock(name='parent')
    parent.request.app = MagicMock(name='app')
    parent.app = parent.request.app
    name = 'name'

    return Resource(parent, name)


def test_Resource_getitem(loop, res_simple):  # noqa
    traverser = res_simple['a']
    assert isinstance(traverser, Traverser)
    assert traverser.resource is res_simple
    assert traverser.path == ('a',)


def test_Resource_getchild(loop, res_simple):  # noqa
    assert loop.run_until_complete(res_simple.__getchild__('a')) is None


def test_InitCoroMixin(loop):  # noqa
    class Res(InitCoroMixin, Resource):
        calls_init = 0
        calls_ainit = 0

        def __init__(self, parent, name):
            super().__init__(parent, name)
            self.calls_init += 1

        @asyncio.coroutine
        def __ainit__(self):
            self.calls_ainit += 1

    coro = Res(None, 'name')

    assert asyncio.iscoroutine(coro)

    res = loop.run_until_complete(coro)

    assert isinstance(res, Res)
    assert res.calls_init == 1
    assert res.calls_ainit == 1


def test_DispatchResource(loop, app):  # noqa
    class Res(Resource):
        pass

    class CoroRes(InitCoroMixin, Resource):
        calls_ainit = 0

        @asyncio.coroutine
        def __ainit__(self):
            self.calls_ainit += 1

    add_child(app, 'aiohttp_traversal.ext.resources.Root', 'simple', Res)
    add_child(app, Root, 'coro', CoroRes)

    request = MagicMock(name='request')
    request.app = app

    root = Root(app)

    res_simple = loop.run_until_complete(iter(root['simple']))
    assert isinstance(res_simple, Res)
    assert res_simple.name == 'simple'
    assert res_simple.__parent__ is root

    res_coro = loop.run_until_complete(iter(root['coro']))
    assert isinstance(res_coro, CoroRes)
    assert res_coro.name == 'coro'
    assert res_coro.__parent__ is root
    assert res_coro.calls_ainit == 1

    with pytest.raises(KeyError):
        loop.run_until_complete(iter(root['not_exist']))
