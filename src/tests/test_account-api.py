from datetime import timedelta

from account.models import Contact, User

from django.urls import reverse


def test_get_rates_api_not_auth(client):
    url = reverse('api-account:users')
    response = client.get(url)
    assert response.status_code == 401
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data['detail'] == 'Authentication credentials were not provided.'


def test_get_api_users_registered_user(api_client, user):
    url = reverse('api-account:users')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 403
    assert response.json()['detail'] == 'You do not have permission to perform this action.'


def test_get_api_users_admin(admin_client):
    url = reverse('api-account:users')
    response = admin_client.get(url)
    assert response.status_code == 200
    assert response['allow'] == 'GET, POST, HEAD, OPTIONS'
    assert response['content-type'] == 'application/json'


def test_post_api_get_token_not_user(client):
    url = reverse('token_obtain_pair')
    payload = {
        'username': 'nosuchuser',
        'password': 'nosuchuser'
    }
    response = client.post(url, payload)
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == 'No active account found with the given credentials'


def test_rates_api_filters_post(admin_client):
    url = reverse('api-account:users')
    initial_count = User.objects.count()
    payload = {
        'username': 'test',
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test@example.com',
        'is_active': 'true',
        'date_joined': '2020-07-22T06:47:12.646Z',
        format: 'json'
    }
    response = admin_client.post(url, payload)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data['username'] == 'test'
    assert response_data['first_name'] == 'test'
    assert response_data['last_name'] == 'test'
    assert response_data['email'] == 'test@example.com'
    assert response_data['is_active']
    assert User.objects.count() == initial_count + 1


def test_users_account_api_put(admin_client):
    url = reverse('api-account:users')
    user = User.objects.first()
    path = '/'
    url = url + str(user.id) + path
    payload = {
        "id": f"{user.id}",
        "username": "user",
        "first_name": "user",
        "last_name": "user",
        "email": "user@example.com",
        "is_active": "true",
        "date_joined": "2020-07-22T07:58:22.701000Z"
    }
    response = admin_client.put(url, payload, content_type='application/json')
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'


def test_rates_api_filters_created_range(admin_client):
    url = reverse('api-account:users')
    date = User.objects.last().date_joined
    created_after = date - timedelta(minutes=5)
    created_before = date + timedelta(minutes=5)
    payload = {
        'date_joined': f'{str(created_after)}, {str(created_before)}'
    }
    response = admin_client.get(url, payload)
    assert response.status_code == 200
    assert response['content-type'] == 'application/json'


def test_users_account_api_delete(admin_client):
    url = reverse('api-account:users')
    user = User.objects.first()
    path = '/'
    url = url + str(user.id) + path
    initial_count = User.objects.count()
    response = admin_client.delete(url)
    assert response.status_code == 204
    assert User.objects.count() == initial_count - 1
    assert response['content-length'] == '0'


def test_contact_form_api_not_auth(client):
    url = reverse('api-account:contact')
    response = client.get(url)
    assert response.status_code == 401
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json['detail'] == 'Authentication credentials were not provided.'


def test_contact_form_api_auth(api_client, user):
    url = reverse('api-account:contact')
    api_client.login(user.username, user.raw_password)
    response = api_client.get(url)
    assert response.status_code == 200


def test_contact_form_api_post(api_client, user):
    url = reverse('api-account:contact')
    api_client.login(user.username, user.raw_password)

    initial_count = Contact.objects.count()
    payload = {
        'email_from': f'{user.email}',
        'title': 'some_text',
        'message': 'some_text',
        format: 'json'
    }
    response = api_client.post(url, payload)
    assert response.status_code == 201
    assert Contact.objects.count() == initial_count + 1


def test_contact_form_api_get_filter_contains(api_client, user):
    url = reverse('api-account:contact')
    api_client.login(user.username, user.raw_password)
    payload = {
        'title': 'some_te',
        'message': 'some',
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['results'][0]['title'] == 'some_text'
    assert response_data['results'][0]['message'] == 'some_text'


def test_contact_form_api_get_filter_range(api_client, user):
    url = reverse('api-account:contact')
    api_client.login(user.username, user.raw_password)
    date = Contact.objects.last().created
    created_after = date - timedelta(minutes=5)
    created_before = date + timedelta(minutes=5)
    payload = {
        'created__range': f'{str(created_after)}, {str(created_before)}'
    }
    response = api_client.get(url, payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['results'][0]['title'] == 'some_text'
    assert response_data['results'][0]['message'] == 'some_text'
