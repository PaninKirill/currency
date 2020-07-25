import json
import os

from django.conf import settings

from rate.models import Rate
from rate.tasks import (
    parse_alfabank,
    parse_monobank,
    parse_nbu,
    parse_pivdenniy,
    parse_privatbank,
    parse_pumb,
    parse_vkurse,
)


class Response:
    pass


def test_privat(mocker):
    def mock():
        res = [
            {
                "ccy": "RUR",
                "base_ccy": "UAH",
                "buy": "0.28000",
                "sale": "0.32000"
            },
            {
                "ccy": "EUR",
                "base_ccy": "UAH",
                "buy": "19.20000",
                "sale": "20.00000"
            },
            {
                "ccy": "USD",
                "base_ccy": "UAH",
                "buy": "15.50000",
                "sale": "15.85000"
            }
        ]
        response = Response()
        response.json = lambda: res
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_privatbank()
    assert Rate.objects.count() == rate_initial_count + 3
    parse_privatbank()
    assert Rate.objects.count() == rate_initial_count + 3


def test_monobank(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'monobank.json')
        with open(path) as file:
            content = json.load(file)

        response = Response()
        response.json = lambda: content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_monobank()
    assert Rate.objects.count() == rate_initial_count + 3
    parse_monobank()
    assert Rate.objects.count() == rate_initial_count + 3


def test_vkurse(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'vkurse.json')
        with open(path) as file:
            content = json.load(file)

        response = Response()
        response.json = lambda: content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_vkurse()
    assert Rate.objects.count() == rate_initial_count + 3
    parse_vkurse()
    assert Rate.objects.count() == rate_initial_count + 3


def test_alfabank(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'alfabank.html')
        with open(path, encoding='utf-8') as file:
            content = file.read()

        response = Response()
        response.text = content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_alfabank()
    assert Rate.objects.count() == rate_initial_count + 2
    parse_alfabank()
    assert Rate.objects.count() == rate_initial_count + 2


def test_pumb(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'pumb.html')
        with open(path, encoding='utf-8') as file:
            content = file.read()

        response = Response()
        response.text = content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_pumb()
    assert Rate.objects.count() == rate_initial_count + 3
    parse_pumb()
    assert Rate.objects.count() == rate_initial_count + 3


def test_nbu(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'nbu.json')
        with open(path) as file:
            content = json.load(file)

        response = Response()
        response.json = lambda: content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_nbu()
    assert Rate.objects.count() == rate_initial_count + 2
    parse_nbu()
    assert Rate.objects.count() == rate_initial_count + 2


def test_pivdenniy(mocker):
    def mock():
        path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'pivdenniy.html')
        with open(path, encoding='utf-8') as file:
            content = file.read()

        response = Response()
        response.text = content
        return response

    requests_get_patcher = mocker.patch('requests.get')
    requests_get_patcher.return_value = mock()
    rate_initial_count = Rate.objects.count()
    parse_pivdenniy()
    assert Rate.objects.count() == rate_initial_count + 3
    parse_pivdenniy()
    assert Rate.objects.count() == rate_initial_count + 3
