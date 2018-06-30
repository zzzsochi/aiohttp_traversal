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


@asyncio.coroutine
def test_middleware(aiohttp_client, loop):
    mod = load_example('2-middleware')
    app = mod.create_app(loop)
    client = yield from aiohttp_client(app)

    # Hello
    resp = yield from client.get('/')
    assert resp.status == 200

    data = yield from resp.json()
    assert data == {'counter': 1}

    # 404
    resp = yield from client.get('/thing')
    assert resp.status == 404

    data = yield from resp.json()
    assert data == {'error': 'not_found', 'reason': 'Not Found'}
