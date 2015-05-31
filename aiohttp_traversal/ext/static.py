""" DO NOT USE IN PRODUCTION!!!
"""

import os
import asyncio
import mimetypes
import warnings
import logging
from collections import namedtuple

from aiohttp.web import Response, HTTPNotFound
from resolver_deco import resolver

from .resources import Resource, add_child
from .views import View

log = logging.getLogger(__name__)


StaticInfo = namedtuple('StaticInfo', ('path', 'content_type', 'data'))


class StaticResource(Resource):
    path = None

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self.path = os.path.abspath(self.path)

    @asyncio.coroutine
    def __getchild__(self, name):
        return None

    def get(self, path):
        path = os.path.join(self.path, path)

        if not os.path.isfile(path):
            raise HTTPNotFound()

        ext = os.path.splitext(path)[1]
        ct = mimetypes.types_map.get(ext, 'application/octet-stream')

        with open(path, 'rb') as f:
            return StaticInfo(path, ct, f.read())


class StaticView(View):
    @asyncio.coroutine
    def __call__(self):
        if self.request.tail:
            path = os.path.join(*self.request.tail)
        else:
            path = ''

        info = self.resource.get(path)

        return Response(
            body=info.data,
            headers={'Content-Type': info.content_type},
        )


def prepare_static_view(app):
    warnings.warn("Do not use this module in production!")
    app.router.bind_view(StaticResource, StaticView, tail='*')


@resolver('parent', 'resource_class')
def add_static(app, parent, name, path, resource_class=StaticResource):
    """ Add resource for serve static
    """
    warnings.warn("Do not use this module in production!")
    SRes = type(resource_class.__name__, (resource_class,), {'path': path})
    add_child(app, parent, name, SRes)
