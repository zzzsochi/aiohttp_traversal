import asyncio

import pytest
from aiohttp.web import Application

from aiohttp_traversal.abc import AbstractResource
from aiohttp_traversal.router import TraversalRouter
from aiohttp_traversal.traversal import Traverser


@pytest.yield_fixture
def loop():
    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def root_factory():
    return lambda app: Resource(parent=None, name='ROOT')


class Resource(AbstractResource):
    __parent__ = None

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.name = name

    def __getitem__(self, name):
        return Traverser(self, (name,))

    async def __getchild__(self, name):
        if name == 'not':
            return None
        else:
            return Resource(self, name)

    def __repr__(self):
        return '<resource {!r}>'.format(self.name)


@pytest.fixture
def router(root_factory):
    return TraversalRouter(root_factory=root_factory)


@pytest.fixture
def app(loop, router):
    return Application(loop=loop, router=router)


@pytest.fixture
def root(app, root_factory):
    return root_factory(app)
