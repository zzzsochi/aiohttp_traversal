import json
import asyncio

from aiohttp.web import Response, StreamResponse
from aiohttp.web import HTTPMethodNotAllowed

from aiohttp_traversal.abc import AbstractView


class View(AbstractView):
    def __init__(self, request, resource, tail):
        self.request = request
        self.resource = resource
        self.tail = tail

    @asyncio.coroutine
    def __call__(self):
        raise NotImplementedError


class MethodsView(View):
    methods = frozenset()  # {'get', 'post', 'put', 'patch', 'delete', 'option'}

    @asyncio.coroutine
    def __call__(self):
        method = self.request.method.lower()

        if method in self.methods:
            return (yield from getattr(self, method)())
        else:
            raise HTTPMethodNotAllowed(method, self.methods)

    @asyncio.coroutine
    def get(self):
        raise NotImplementedError

    @asyncio.coroutine
    def post(self):
        raise NotImplementedError

    @asyncio.coroutine
    def put(self):
        raise NotImplementedError

    @asyncio.coroutine
    def patch(self):
        raise NotImplementedError

    @asyncio.coroutine
    def delete(self):
        raise NotImplementedError

    @asyncio.coroutine
    def option(self):
        raise NotImplementedError


class RESTView(MethodsView):
    @asyncio.coroutine
    def __call__(self):
        data = yield from super().__call__()

        if isinstance(data, StreamResponse):
            return data
        else:
            return Response(
                body=json.dumps(data).encode('utf8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
            )
