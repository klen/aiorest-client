import asyncio
import pytest


@pytest.fixture
def loop():
    return asyncio.get_event_loop()


def test_api_descriptor():
    from aiorest_client import APIDescriptor

    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '/resources/22'
        assert kwargs['data']
        assert kwargs['params']

    api = APIDescriptor(request)
    api.resources[22].post(params={'q': 'test_q'}, data={'f': 'test_f'})

    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '/res/43/get'
        assert kwargs['data'] == {'q': 'test_q'}

    api = APIDescriptor(request)
    api.res[43]['get'].post({'q': 'test_q'})


def test_api_client(loop):
    from aiorest_client import APIClient, APIError, __version__

    client = APIClient('https://api.github.com', headers={
        'User-Agent': 'AIO REST CLIENT %s' % __version__
    })
    with pytest.raises(APIError):
        res = loop.run_until_complete(client.api.events.post({'name': 'New Event'}))

    # Initialize a session
    loop.run_until_complete(client.startup())

    res = loop.run_until_complete(client.api.users.klen())
    assert res
    assert isinstance(res, dict)

    res = loop.run_until_complete(client.api.users.klen(parse=False))
    assert res.status == 200

    res = loop.run_until_complete(client.api.users.klen(close=True))
    assert res.status == 200
    with pytest.raises(Exception):
        loop.run_until_complete(res.json())
