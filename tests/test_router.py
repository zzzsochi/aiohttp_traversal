from unittest.mock import Mock

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from aiohttp_traversal.traversal import find_root, lineage
from aiohttp_traversal.router import MatchInfo, ViewNotResolved

from .helpers import *


@pytest.fixture
def request(app):
    request = Mock(name='request')
    request.app = app
    request.path = '/'
    return request


def test_resolve(loop, router, request, root):
    request.path = '/a/b/c'

    @asyncio.coroutine
    def traverse(request):
        return ('res', 'tail')

    def resolve_view(res, tail):
        @asyncio.coroutine
        def view_call():
            return 'view_result'

        mock = Mock(name='view')
        mock.name = 'view'
        mock.return_value = view_call()
        return mock

    router.traverse = traverse
    router.resolve_view = resolve_view
    mi = loop.run_until_complete(router.resolve(request))

    assert isinstance(mi, MatchInfo)
    assert mi._view.name == 'view'
    assert mi.route is None

    result = loop.run_until_complete(mi.handler(request))
    assert result == 'view_result'


def test_resolve__not_found(loop, router, request, root):
    request.path = '/a/b/c'

    @asyncio.coroutine
    def traverse(request):
        return ('res', 'tail')

    def resolve_view(res, tail):
        raise ViewNotResolved(res, tail)

    router.traverse = traverse
    router.resolve_view = resolve_view

    with pytest.raises(HTTPNotFound):
        loop.run_until_complete(router.resolve(request))


def test_traverse(loop, router, request):
    request.path = '/a/b/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert res.name == 'c'
    assert not tail
    assert len(list(lineage(res))) == 4
    assert find_root(res).name == 'ROOT'


def test_traverse_with_tail(loop, router, request, ):
    request.path = '/a/b/not/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert res.name == 'b'
    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 3
    assert find_root(res).name == 'ROOT'


def test_traverse_root(loop, router, request):
    request.path = '/'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert tail == ()
    assert len(list(lineage(res))) == 1
    assert find_root(res) is res
    assert res.name == 'ROOT'


def test_traverse_root_with_tail(loop, router, request):
    request.path = '/not/c'

    res, tail = loop.run_until_complete(router.traverse(request))

    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 1
    assert find_root(res).name == 'ROOT'


def test_set_root_factory(router):
    assert router._root_factory
    new_root_class = Mock(name='root')
    router.set_root_factory(new_root_class)
    assert router._root_factory is new_root_class


def test_get_root(loop, router):
    assert loop.run_until_complete(router.get_root('request')).name == 'ROOT'


@pytest.fixture
def Res():
    return type('res', (), {})


@pytest.fixture
def View():
    class View:
        def __init__(self, resource):
            self.resource = resource

    return View


def test_resolve_view(router, Res, View):
    res = Res()
    tail = ('a', 'b')
    router.resources[Res] = {'views': {tail: View}}

    view = router.resolve_view(res, tail)

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__asterisk(router, Res, View):
    res = Res()
    router.resources[Res] = {'views': {'*': View}}

    view = router.resolve_view(res, ('a', 'b'))

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__mro(router, Res, View):
    class SubRes(Res):
        pass

    res = SubRes()
    router.resources[Res] = {'views': {'*': View}}

    view = router.resolve_view(res, '*')

    assert isinstance(view, View)
    assert view.resource is res


def test_resolve_view__mro_invert(router, Res, View):
    class SubRes(Res):
        pass

    res = Res()
    router.resources[SubRes] = {'views': {'*': View}}

    with pytest.raises(ViewNotResolved):
        router.resolve_view(res, '*')


def test_resolve_view__not_resolved(router):
    with pytest.raises(ViewNotResolved):
        router.resolve_view(str, ())


def test_bind_view(router, Res, View):
    router.bind_view(Res, View)
    assert router.resources[Res]['views'][()] is View


def test_bind_view__tail_str(router, Res, View):
    router.bind_view(Res, View, '/a/b')
    assert router.resources[Res]['views'][('a', 'b')] is View


def test_bind_view__tail_str_asterisk(router, Res, View):
    router.bind_view(Res, View, '*')
    assert router.resources[Res]['views']['*'] is View


def test_repr(router):
    repr(router)
