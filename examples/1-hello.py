"""
Hello World application

After start, check urls:

    * GET localhost:8080/
    * GET localhost:8080/json

"""
import asyncio

from aiohttp.web import Application, Response

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


def main():
    loop = asyncio.get_event_loop()

    app = Application(router=TraversalRouter())  # create main application instance
    app.router.set_root_factory(Root)  # set root factory
    app.router.bind_view(Root, HelloView)  # add view for '/'
    app.router.bind_view(Root, HelloJSON, 'json')  # add view for '/json'

    # listening socket
    handler = app.make_handler()
    f = loop.create_server(handler, 'localhost', 8080)
    srv = loop.run_until_complete(f)

    try:
        loop.run_forever()  # run event loop
    except KeyboardInterrupt:
        pass
    finally:
        # stopping
        loop.run_until_complete(handler.finish_connections(timeout=5.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.finish())
        loop.close()


if __name__ == '__main__':
    main()
