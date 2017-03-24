from unittest.mock import Mock
import asyncio

import pytest

from aiohttp.web import Response
from aiohttp.web import HTTPMethodNotAllowed

from aiohttp_traversal.ext.views import (
    View,
    MethodsView,
    RESTView,
)


def test_View_init():  # noqa
    request = Mock(name='request')
    resource = Mock(name='resource')
    tail = ('ta', 'il')
    view = View(request, resource, tail)
    assert view.request is request
    assert view.resource is resource
    assert view.tail is tail


@pytest.fixture
def MVw(request):  # noqa
    class MVw(MethodsView):
        methods = {'get', 'post'}

        @asyncio.coroutine
        def get(self):
            return 'data'

    return MVw


def test_MethodsView_call(loop, MVw):  # noqa
    request = Mock(name='request')
    request.method = 'GET'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    resp = loop.run_until_complete(MVw(request, resource, tail)())
    assert resp == 'data'


def test_MethodsView_call__not_implemented(loop, MVw):  # noqa
    request = Mock(name='request')
    request.method = 'POST'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    with pytest.raises(NotImplementedError):
        loop.run_until_complete(MVw(request, resource, tail)())


def test_MethodsView_call__not_allowed(loop, MVw):  # noqa
    request = Mock(name='request')
    request.method = 'DELETE'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    with pytest.raises(HTTPMethodNotAllowed):
        loop.run_until_complete(MVw(request, resource, tail)())


@pytest.fixture
def RVw():  # noqa
    class RVw(RESTView):
        methods = {'get', 'post'}

        @asyncio.coroutine
        def get(self):
            return {'key': 'value'}

        @asyncio.coroutine
        def post(self):
            return Response()

    return RVw


def test_RESTView__dict(loop, RVw):  # noqa
    request = Mock(name='request')
    request.method = 'GET'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    resp = loop.run_until_complete(RVw(request, resource, tail)())
    assert isinstance(resp, Response)


def test_RESTView__response(loop, RVw):  # noqa
    request = Mock(name='request')
    request.method = 'POST'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    resp = loop.run_until_complete(RVw(request, resource, tail)())
    assert isinstance(resp, Response)


@pytest.fixture
def RVobj():  # noqa
    class RVobj(RESTView):
        methods = {'get', 'post'}

        def serialize(self, data):
            return data.upper().encode('utf8')

        @asyncio.coroutine
        def get(self):
            return "test"

    return RVobj


def test_RESTView__object(loop, RVobj):  # noqa
    request = Mock(name='request')
    request.method = 'GET'
    resource = Mock(name='resource')
    tail = ('ta', 'il')

    resp = loop.run_until_complete(RVobj(request, resource, tail)())
    assert isinstance(resp, Response)
    assert resp.body == b'TEST'
