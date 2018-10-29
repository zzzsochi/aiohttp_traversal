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

    async def __call__(self):
        raise NotImplementedError()


class MethodsView(View):
    methods = frozenset()  # {'get', 'post', 'put', 'patch', 'delete', 'option'}

    async def __call__(self):
        method = self.request.method.lower()

        if method in self.methods:
            return await getattr(self, method)()
        else:
            raise HTTPMethodNotAllowed(method, self.methods)

    async def get(self):
        raise NotImplementedError

    async def post(self):
        raise NotImplementedError

    async def put(self):
        raise NotImplementedError

    async def patch(self):
        raise NotImplementedError

    async def delete(self):
        raise NotImplementedError

    async def option(self):
        raise NotImplementedError


class RESTView(MethodsView):
    def serialize(self, data):
        """ Serialize data to JSON.

        You can owerride this method if you data cant be serialized
        standart json.dumps routine.
        """
        return json.dumps(data).encode('utf8')

    async def __call__(self):
        data = await super().__call__()

        if isinstance(data, StreamResponse):
            return data
        else:
            return Response(
                body=self.serialize(data),
                headers={'Content-Type': 'application/json; charset=utf-8'},
            )
