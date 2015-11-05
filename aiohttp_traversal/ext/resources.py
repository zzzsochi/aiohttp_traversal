import asyncio
import logging

from resolver_deco import resolver

from aiohttp_traversal.abc import AbstractResource
from aiohttp_traversal.traversal import Traverser

log = logging.getLogger(__name__)


class Resource(AbstractResource):
    _parent = None
    name = None
    app = None
    setup = None

    def __init__(self, parent, name):
        self._parent = parent
        self.name = str(name)

        if parent is not None:
            self.app = parent.app
            self.setup = self.app.router.resources.get(self.__class__)

    @property
    def __parent__(self):
        return self._parent

    def __getitem__(self, name):
        return Traverser(self, (name,))

    @asyncio.coroutine
    def __getchild__(self, name):
        return None


class InitCoroMixin:
    """ Mixin for create initialization coroutine
    """
    def __new__(cls, *args, **kwargs):
        """ This is magic!
        """
        instance = super().__new__(cls)

        @asyncio.coroutine
        def coro():
            instance.__init__(*args, **kwargs)
            yield from instance.__ainit__()
            return instance

        return coro()

    @asyncio.coroutine
    def __ainit__(self):
        raise NotImplementedError


class DispatchMixin:
    @asyncio.coroutine
    def __getchild__(self, name):
        if (self.setup is not None and
                'children' in self.setup and
                name in self.setup['children']):

            res = self.setup['children'][name](self, name)

            if asyncio.iscoroutine(res):
                return (yield from res)
            else:
                return res
        else:
            return None


class DispatchResource(DispatchMixin, Resource):
    pass


class Root(DispatchResource):
    def __init__(self, app, *args, **kwargs):
        super().__init__(parent=None, name=None)
        self.app = app
        self.args = args
        self.kwargs = kwargs
        self.setup = self.app.router.resources.get(self.__class__)


@resolver('parent', 'child')
def add_child(app, parent, name, child):
    """ Add child resource for dispatch-resources
    """
    if not issubclass(parent, DispatchMixin):
        raise ValueError("{!r} is not a DispatchMixin subclass"
                         "".format(parent))

    parent_setup = app.router.resources.setdefault(parent, {})
    parent_setup.setdefault('children', {})[name] = child
