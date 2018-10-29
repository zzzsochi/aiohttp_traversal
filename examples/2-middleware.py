"""
REST-like requests counter application with JSON error responces.

Start this:

    $ python3 2-middleware.py

Or use aiohttp_devtools:

    $ adev runserver 2-middleware.py --app-factory create_app

After start, check urls:

    * GET localhost:8000/
    * GET localhost:8000/thing
    * POST localhost:8000/
"""
import asyncio

import aiohttp
from aiohttp.web import Application, run_app

from aiohttp_traversal.router import TraversalRouter
from aiohttp_traversal.ext.views import RESTView
from aiohttp_traversal.ext.resources import Root


class Counter(RESTView):
    methods = {'get'}

    @asyncio.coroutine
    def get(self):
        self.request.app['counter'] += 1
        return dict(counter=self.request.app['counter'])


async def json_error_middleware(app, handler):
    async def middleware_handler(request):
        try:
            resp = await handler(request)
            if isinstance(resp, aiohttp.web.HTTPException):
                raise resp
        except aiohttp.web.HTTPNoContent:
            raise
        except aiohttp.web.HTTPNotFound as exc:
            return error_response(404, 'not_found', exc.reason, exc.headers)
        except aiohttp.web.HTTPMethodNotAllowed as exc:
            return error_response(405, 'not_allowed', exc.reason, exc.headers)
        else:
            return resp
    return middleware_handler


def error_response(status, error, reason, headers) -> aiohttp.web.Response:
    if headers is not None:
        headers.pop('Content-Type', None)
    return aiohttp.web.json_response(
        data={'error': error, 'reason': reason},
        headers=headers,
        status=status,
    )


def create_app():
    app = Application(router=TraversalRouter())

    app.middlewares.append(json_error_middleware)

    app.router.set_root_factory(lambda request, app=app: Root(app))
    app.router.bind_view(Root, Counter)

    app['counter'] = 0

    return app


if __name__ == '__main__':
    app = create_app()
    run_app(app, port=8000)
