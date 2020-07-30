from account.models import User

from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse

from faker import Faker

import pytest

from pytest_django.fixtures import _django_db_fixture_helper

from rest_framework.test import APIClient


@pytest.fixture(scope='session', autouse=True)
def db_session(request, django_db_setup, django_db_blocker):
    """
    Changed scope to 'session'
    """
    if 'django_db_reset_sequences' in request.funcargnames:
        request.getfixturevalue('django_db_reset_sequences')
    if 'transactional_db' in request.funcargnames \
            or 'live_server' in request.funcargnames:
        request.getfixturevalue('transactional_db')
    else:
        _django_db_fixture_helper(request, django_db_blocker, transactional=False)


@pytest.mark.django_db(transaction=True)
@pytest.fixture(scope='session', autouse=True)
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'rates.json')


@pytest.fixture(scope='function')
def api_client():
    client = APIClient()

    def login(username, password):
        url = reverse('token_obtain_pair')
        payload = {
            'username': f'{username}',
            'password': f'{password}'
        }
        response = client.post(url, payload)
        assert response.status_code == 200
        access = response.json()['access']
        client.credentials(HTTP_AUTHORIZATION=f'JWT {access}')

    client.login = login

    yield client


@pytest.fixture(scope='session', autouse=True)
def user():
    username = 'user'
    password = '1234567asd'
    email = 'user@mail.com'
    initial_user = User.objects.create(username=username, password=password, email=email)
    initial_user.set_password(password)
    initial_user.save()

    initial_user.raw_password = password

    yield initial_user


@pytest.fixture(scope='session')
def fake():
    yield Faker()


@pytest.fixture(scope='session', autouse=True)
def clear_session():
    cache.clear()
    yield
    cache.clear()
