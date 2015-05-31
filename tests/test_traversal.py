import asyncio

import pytest

from aiohttp_traversal.traversal import (
    traverse,
    find_root,
    lineage,
)

from .helpers import *


@pytest.fixture
def res_c(loop, root):
    return loop.run_until_complete(iter(root['a']['b']['c']))


def test_traverse(loop, root):
    res, tail = loop.run_until_complete(traverse(root, ('a', 'b', 'c')))
    assert res.name == 'c'
    assert not tail
    assert len(list(lineage(res))) == 4


def test_traverse_with_tail(loop, root):
    res, tail = loop.run_until_complete(traverse(root, ('a', 'b', 'not', 'c')))
    assert res.name == 'b'
    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 3


def test_traverser(loop, root):
    res = loop.run_until_complete(iter(root['a']['b']['c']))
    assert res.name == 'c'
    assert len(list(lineage(res))) == 4


def test_traverser_yield_from(loop, root):
    @asyncio.coroutine
    def coro():
        return (yield from root['a']['b']['c'])

    res = loop.run_until_complete(coro())
    assert res.name == 'c'
    assert len(list(lineage(res))) == 4


def test_traverser_with_tail(loop, root):
    with pytest.raises(KeyError):
        loop.run_until_complete(iter(root['a']['b']['not']))


def test_lineage(root, res_c):
    l = list(lineage(res_c))
    assert l[0] is res_c
    assert l[-1] is root
    assert len(l) is 4


def test_find_root(root, res_c):
    assert find_root(res_c) is root
