import asyncio
import aiohttp
import pytest
import mock


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
    assert client.Error

    with pytest.raises(APIError):
        res = loop.run_until_complete(client.api.events.post({'name': 'New Event'}))

    with pytest.raises(ValueError):

        @client.middleware
        def test_middleware(method, url, options):
            options['headers']['X-Test'] = 'passed'
            return method, url, options

    @client.middleware
    async def test_middleware(method, url, options):
        options['headers']['X-Test'] = 'passed'
        return method, url, options

    assert test_middleware

    # Initialize a session
    loop.run_until_complete(client.startup())

    async def response(value):
        res = aiohttp.web.Response(content_type='application/json')
        async def json():
            return value
        res.json = json
        res.close = mock.Mock()
        return res

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen())
        assert res == {'test': 'passed'}

    assert not 'X-Test' in client.defaults['headers']

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen(parse=False))
        assert res.status == 200

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen(close=True))
        assert res.status == 200
        assert res.close.called
