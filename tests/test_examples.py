import os
import pathlib
from importlib.machinery import SourceFileLoader


def load_example(name):
    here = pathlib.Path(os.path.dirname(__file__))
    path = here / '..' / 'examples' / (name + '.py')
    mod = SourceFileLoader(name, str(path)).load_module()
    return mod


async def test_hello(aiohttp_client, loop):
    mod = load_example('1-hello')
    app = mod.create_app(loop)
    client = await aiohttp_client(app)

    # HelloView
    resp = await client.get('/')
    assert resp.status == 200

    body = await resp.text()
    assert body == 'Hello World!'

    # HelloJSON
    resp = await client.get('/json')
    assert resp.status == 200

    data = await resp.json()
    assert data == {'text': 'Hello World!'}


async def test_middleware(aiohttp_client, loop):
    mod = load_example('2-middleware')
    app = mod.create_app(loop)
    client = await aiohttp_client(app)

    # Hello
    resp = await client.get('/')
    assert resp.status == 200

    data = await resp.json()
    assert data == {'counter': 1}

    # 404
    resp = await client.get('/thing')
    assert resp.status == 404

    data = await resp.json()
    assert data == {'error': 'not_found', 'reason': 'Not Found'}
