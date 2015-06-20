import asyncio
import logging

from aiohttp.abc import AbstractRouter, AbstractMatchInfo
from aiohttp.web_exceptions import HTTPNotFound

from resolver_deco import resolver
from .traversal import traverse

log = logging.getLogger(__name__)


class ViewNotResolved(Exception):
    """ Raised from Application.resolve_view
    """
    def __init__(self, resource, tail):
        super().__init__(resource, tail)
        self.resource = resource
        self.tail = tail


class MatchInfo(AbstractMatchInfo):
    route = None

    def __init__(self, view):
        self._view = view

    def handler(self, request):
        return self._view()


class _NotFoundMatchInfo(AbstractMatchInfo):
    route = None

    def __init__(self):
        pass

    def handler(self, request):
        raise HTTPNotFound()


class TraversalRouter(AbstractRouter):
    _root_factory = None

    @resolver('root_factory')
    def __init__(self, root_factory=None):
        self.set_root_factory(root_factory)
        self.resources = {}

    @asyncio.coroutine
    def resolve(self, request):
        resource, tail = yield from self.traverse(request)
        request.resource = resource
        request.tail = tail

        try:
            view = self.resolve_view(resource, tail)
        except ViewNotResolved:
            return _NotFoundMatchInfo()

        return MatchInfo(view)

    @asyncio.coroutine
    def traverse(self, request):
        path = tuple(p for p in request.path.split('/') if p)
        root = yield from self.get_root(request)

        if path:
            return (yield from traverse(root, path))
        else:
            return root, path

    @resolver('root_factory')
    def set_root_factory(self, root_factory):
        """ Set root resource class

        Analogue of the "set_root_factory" method from pyramid framework.
        """
        self._root_factory = root_factory

    @asyncio.coroutine
    def get_root(self, request):
        """ Create new root resource instance
        """
        return self._root_factory(request)

    @resolver('resource')
    def resolve_view(self, resource, tail=()):
        """ Resolve view for resource and tail
        """
        if isinstance(resource, type):
            resource_class = resource
        else:
            resource_class = resource.__class__

        for rc in resource_class.__mro__[:-1]:
            if rc in self.resources:
                views = self.resources[rc]['views']

                if tail in views:
                    view = views[tail]
                    break

                elif '*' in views:
                    view = views['*']
                    break

        else:
            raise ViewNotResolved(resource, tail)

        return view(resource)

    @resolver('resource', 'view')
    def bind_view(self, resource, view, tail=()):
        """ Bind view for resource
        """
        if isinstance(tail, str) and tail != '*':
            tail = tuple(i for i in tail.split('/') if i)

        setup = self.resources.setdefault(resource, {'views': {}})
        setup['views'][tail] = view

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)
