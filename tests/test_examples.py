import asyncio
import os
import pathlib
from importlib.machinery import SourceFileLoader

import pytest


def load_example(name):
    here = pathlib.Path(os.path.dirname(__file__))
    path = here / '..' / 'examples' / (name + '.py')
    mod = SourceFileLoader(name, str(path)).load_module()
    return mod


@asyncio.coroutine
def test_hello(aiohttp_client, loop):
    mod = load_example('1-hello')
    app = mod.create_app(loop)
    client = yield from aiohttp_client(app)

    # HelloView
    resp = yield from client.get('/')
    assert resp.status == 200

    body = yield from resp.text()
    assert body == 'Hello World!'

    # HelloJSON
    resp = yield from client.get('/json')
    assert resp.status == 200

    data = yield from resp.json()
    assert data == {'text': 'Hello World!'}

