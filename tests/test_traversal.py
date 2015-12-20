import asyncio
import sys

import pytest

from aiohttp_traversal.traversal import (
    traverse,
    find_root,
    lineage,
)


@pytest.fixture
def res_c(loop, root):
    @asyncio.coroutine
    def coro():
        return (yield from root['a']['b']['c'])

    return loop.run_until_complete(coro())


def test_traverse(loop, root):
    @asyncio.coroutine
    def coro():
        return (yield from traverse(root, ('a', 'b', 'c')))

    res, tail = loop.run_until_complete(coro())
    assert res.name == 'c'
    assert not tail
    assert len(list(lineage(res))) == 4


def test_traverse_empty(loop, root):
    @asyncio.coroutine
    def coro():
        return (yield from traverse(root, []))

    res, tail = loop.run_until_complete(coro())
    assert res is root
    assert not tail


def test_traverse_with_tail(loop, root):
    @asyncio.coroutine
    def coro():
        return (yield from traverse(root, ('a', 'b', 'not', 'c')))

    res, tail = loop.run_until_complete(coro())
    assert res.name == 'b'
    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 3


def test_traverser_with_tail(loop, root):
    @asyncio.coroutine
    def coro():
        with pytest.raises(KeyError):
            yield from root['a']['b']['not']

    loop.run_until_complete(coro())


def test_lineage(root, res_c):
    l = list(lineage(res_c))
    assert l[0] is res_c
    assert l[-1] is root
    assert len(l) is 4


def test_find_root(root, res_c):
    assert find_root(res_c) is root


if sys.version_info >= (3, 5):
    from .py35_traversal import *  # noqa
