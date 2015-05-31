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

from ..helpers import *


def test_View_init():
    resource = Mock(name='resource')
    view = View(resource)
    assert view.resource is resource
    assert view.request is resource.request


@pytest.fixture
def MVw(request):
    class MVw(MethodsView):
        methods = {'get', 'post'}

        @asyncio.coroutine
        def get(self):
            return 'data'

    return MVw


def test_MethodsView_call(loop, MVw):
    resource = Mock(name='resource')
    resource.request.method = 'GET'

    resp = loop.run_until_complete(MVw(resource)())
    assert resp == 'data'


def test_MethodsView_call__not_implemented(loop, MVw):
    resource = Mock(name='resource')
    resource.request.method = 'POST'

    with pytest.raises(NotImplementedError):
        loop.run_until_complete(MVw(resource)())


def test_MethodsView_call__not_allowed(loop, MVw):
    resource = Mock(name='resource')
    resource.request.method = 'DELETE'

    with pytest.raises(HTTPMethodNotAllowed):
        loop.run_until_complete(MVw(resource)())


@pytest.fixture
def RVw():
    class RVw(RESTView):
        methods = {'get', 'post'}

        @asyncio.coroutine
        def get(self):
            return {'key': 'value'}

        @asyncio.coroutine
        def post(self):
            return Response()

    return RVw


def test_RESTView__dict(loop, RVw):
    resource = Mock(name='resource')
    resource.request.method = 'GET'

    resp = loop.run_until_complete(RVw(resource)())
    assert isinstance(resp, Response)


def test_RESTView__response(loop, RVw):
    resource = Mock(name='resource')
    resource.request.method = 'POST'

    resp = loop.run_until_complete(RVw(resource)())
    assert isinstance(resp, Response)
