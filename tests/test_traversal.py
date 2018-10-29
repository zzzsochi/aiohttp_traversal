import pytest

from aiohttp_traversal.traversal import traverse, lineage


@pytest.fixture
def res_c(loop, root):
    async def coro():
        return await root['a']['b']['c']

    return loop.run_until_complete(coro())


def test_traverse_await(loop, root):
    async def coro():
        return await traverse(root, ('a', 'b', 'c'))

    res, tail = loop.run_until_complete(coro())
    assert res.name == 'c'
    assert not tail
    assert len(list(lineage(res))) == 4


def test_traverse_await_empty(loop, root):
    async def coro():
        return await traverse(root, [])

    res, tail = loop.run_until_complete(coro())
    assert res is root
    assert not tail


def test_traverse_await_with_tail(loop, root):
    async def coro():
        return await traverse(root, ('a', 'b', 'not', 'c'))

    res, tail = loop.run_until_complete(coro())
    assert res.name == 'b'
    assert tail == ('not', 'c')
    assert len(list(lineage(res))) == 3


def test_traverser_await_with_tail(loop, root):
    # import asyncio
    # @asyncio.coroutine
    async def coro():
        with pytest.raises(KeyError):
            await root['a']['b']['not']

    loop.run_until_complete(coro())
