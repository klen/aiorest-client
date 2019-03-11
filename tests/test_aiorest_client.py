import asyncio
import aiohttp
import pytest
import mock


@pytest.fixture
def loop():
    return asyncio.get_event_loop()


@pytest.fixture
def response():
    def gen(value, content_type='application/json'):
        async def coro():
            res = aiohttp.web.Response(content_type=content_type)

            async def json():
                return value
            res.json = json
            res.close = mock.Mock()
            return res
        return coro()

    return gen


def test_api_descriptor():
    from aiorest_client import APIDescriptor

    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '/resources/22'
        assert kwargs['data']
        assert kwargs['params']

    api = APIDescriptor(request)
    assert api.url == '/'
    api.resources[22].post(params={'q': 'test_q'}, data={'f': 'test_f'})

    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '/res/43/get'
        assert kwargs['data'] == {'q': 'test_q'}

    api = APIDescriptor(request)
    assert api.res[43]['get']['url'].url == '/res/43/get/url'

    api.res[43]['get'].post({'q': 'test_q'})


def test_api_client(loop, response):
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

    # Initialize a session
    loop.run_until_complete(client.startup())
    assert client.api.users.klen.url == 'https://api.github.com/users/klen'

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen())
        assert res == {'test': 'passed'}

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen(parse=False))
        assert res.status == 200

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen(close=True))
        assert res.status == 200
        assert res.close.called

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.repos.klen['aiorest-client'].issues.post({
            'title': 'test issue', 'body': 'Issue Body'
        }))
        mocked.assert_called_with(
            'POST', 'https://api.github.com/repos/klen/aiorest-client/issues',
            data=None,
            headers={
                'User-Agent': 'AIO REST CLIENT %s' % __version__,
            },
            json={'title': 'test issue', 'body': 'Issue Body'},
        )

    @client.middleware
    async def test_middleware(method, url, options):
        options['headers']['X-Test'] = 'passed'
        return method, url, options

    assert test_middleware

    with mock.patch.object(client.session, 'request') as mocked:
        mocked.return_value = response({'test': 'passed'})
        res = loop.run_until_complete(client.api.users.klen())
        assert res == {'test': 'passed'}

        mocked.assert_called_with(
            'GET', 'https://api.github.com/users/klen',
            headers={
                'User-Agent': 'AIO REST CLIENT %s' % __version__,
                'X-Test': 'passed',
            },
        )
    assert 'X-Test' not in client.defaults['headers']


def test_custom_sessions(loop, response):
    from aiorest_client import APIClient

    client = APIClient('https://api.github.com')

    # Initialize a default session
    loop.run_until_complete(client.startup())

    session = aiohttp.ClientSession()

    with mock.patch.object(client.session, 'request') as mocked:
        with mock.patch.object(session, 'request') as mocked2:
            mocked2.return_value = response({'test': 'passed'})
            res = loop.run_until_complete(client.api.users.klen(session=session, close=True))
            assert res is not None
            assert not mocked.called
            assert mocked2.called
