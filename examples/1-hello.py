"""
Hello World application.

Start this:

    $ python3 1-hello.py

Or use aiohttp_devtools:

    $ adev runserver 1-hello.py --app-factory create_app

After start, check urls:

    * GET localhost:8000/
    * GET localhost:8000/json
"""
import asyncio

from aiohttp.web import Application, Response, run_app

from aiohttp_traversal.router import TraversalRouter
from aiohttp_traversal.ext.views import View, RESTView
from aiohttp_traversal.ext.resources import Root


class HelloView(View):
    @asyncio.coroutine
    def __call__(self):
        return Response(text="Hello World!")


class HelloJSON(RESTView):
    methods = {'get'}

    @asyncio.coroutine
    def get(self):
        return dict(text="Hello World!")


def create_app():
    app = Application(router=TraversalRouter())  # create main application instance
    app.router.set_root_factory(lambda request, app=app: Root(app))  # set root factory
    app.router.bind_view(Root, HelloView)  # add view for '/'
    app.router.bind_view(Root, HelloJSON, 'json')  # add view for '/json'

    return app


if __name__ == '__main__':
    app = create_app()
    run_app(app, port=8000)
