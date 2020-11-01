from django.urls import reverse

from rate.models import Rate


def test_get_rates_api_not_auth(client):
    url = reverse('api-rate:rates')
    response = client.get(url)
    assert response.status_code == 401
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data['detail'] == 'Authentication credentials were not provided.'


def test_post_api_get_token_not_user(client):
    url = reverse('token_obtain_pair')
    payload = {
        'username': 'notuser',
        'password': 'notpassword',
    }
    response = client.post(url, payload)
    assert response.status_code == 401
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data['detail'] == 'No active account found with the given credentials'


def test_post_api_get_token(client, user):
    url = reverse('token_obtain_pair')
    payload = {
        'username': f'{user.username}',
        'password': f'{user.raw_password}'
    }
    response = client.post(url, payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['refresh']
    assert response_data['access']


def test_rates_api_auth(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response['allow'] == 'GET, POST, HEAD, OPTIONS'
    assert response['content-type'] == 'application/json'


def test_rates_api_filters_ordering(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    payload = {
        'ordering': '-created',
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'

    params = ['buy', '-buy', 'sale', '-sale', 'created', '-created']
    for param in params:
        payload = {
            'ordering': f'{param}',
        }
        response = api_client.get(url, payload)
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'


def test_rates_api_filters_created_range(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    created_after = '2018-05-25T19:43:48.845779Z'
    created_before = '2020-05-25T19:43:48.845779Z'
    payload = {
        'created__range': f'{created_after}, {created_before}'
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'

    params = ['exact', 'lte', 'lt', 'gt', 'gte']
    for param in params:
        payload = {
            f'created__{param}': f'{created_before}',
        }
        response = api_client.get(url, payload)
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'


def test_rates_api_filters_source_and_currency(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    payload = {
        'source': '1',
        'currency': '1',
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'


def test_rates_api_filters_buy_sale_params(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)

    params = ['exact', 'lte', 'lt', 'gt', 'gte']

    for param in params:
        payload = {
            f'buy__{param}': '25',
        }
        response = api_client.get(url, payload)
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'
        response_data = response.json()
        assert response_data['count'] >= 1

    for param in params:
        payload = {
            f'sale__{param}': '25',
        }
        response = api_client.get(url, payload)
        assert response.status_code == 200
        assert response['content-type'] == 'application/json'
        response_data = response.json()
        assert response_data['count'] >= 1


def test_rates_api_pagination(api_client, user):
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    payload = {
        'page': 1,
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'
    response_data = response.json()
    assert response_data['next']
    assert not response_data['previous']

    payload = {
        'page': 2,
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'
    response_data = response.json()
    assert response_data['next']
    assert response_data['previous']

    # non-existent page
    payload = {
        'page': 654645,
    }
    response = api_client.get(url, payload)
    assert response.status_code == 404


def test_crud_rates_api(api_client, user):
    # GET
    url = reverse('api-rate:rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'

    # POST
    initial_count = Rate.objects.count()
    payload = {
        'sale': '23.23',
        'buy': '25.25',
        'source': '1',
        'currency': '1',
        format: 'json'
    }
    response = api_client.post(url, payload)
    assert response.status_code == 201
    assert Rate.objects.count() == initial_count + 1
    assert response['content-type'] == 'application/json'

    # GET
    rate = Rate.objects.last()
    path = '/'
    url = url + str(rate.id) + path
    response = api_client.get(url)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'
    response_data = response.json()
    assert len(response_data) > 2

    # PUT
    payload = {
        'sale': '22.22',
        'buy': '23.23',
        'source': '1',
        'currency': '1',
        format: 'json'
    }
    response = api_client.put(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'

    # DELETE
    initial_count = Rate.objects.count()
    response = api_client.delete(url)
    assert response.status_code == 204
    assert Rate.objects.count() == initial_count - 1
    assert response['content-length'] == '0'


def test_get_latest_rates_api_auth(api_client, user):
    url = reverse('api-rate:latest_rates')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response['allow'] == 'GET, HEAD, OPTIONS'
    assert response['content-type'] == 'application/json'
    assert response.json()['count'] == 19


def test_get_latest_rates_api_not_auth(client):
    url = reverse('api-rate:latest_rates')
    response = client.get(url)
    assert response.status_code == 401
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data['detail'] == 'Authentication credentials were not provided.'
