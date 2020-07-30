from django.urls import reverse

from rate.models import Rate
from rate.utils import to_decimal


def test_index_page(client):
    url = reverse('index')
    response = client.get(url)
    assert response.status_code == 200


def test_rate_list(client):
    url = reverse('rate:list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context_data['charts_data']) != 0


def test_rate_list_filter_ordering(client):
    url = reverse('rate:list')
    filter_params = (
        'created',
        '-created',
        'sale',
        '-sale',
        'buy',
        '-buy',
    )
    for param in filter_params:
        response = client.get(url, {'ordering': param})
        assert response.status_code == 200


def test_rate_list_filter_date(client):
    url = reverse('rate:list')
    created_after = '2020-06-08'
    created_before = '2020-06-17'
    response = client.get(
        url, {
            'created_after': {created_after},
            'created_before': {created_before}
        }
    )
    assert response.status_code == 200


def test_rate_list_filter_source(client):
    url = reverse('rate:list')
    source = 1
    response = client.get(url, {'source': {source}})
    assert response.status_code == 200


def test_rate_list_filter_currency(client):
    url = reverse('rate:list')
    currency = 2
    response = client.get(url, {'currency': {currency}})
    assert response.status_code == 200


def test_rate_list_pagination(client):
    url = reverse('rate:list')
    response = client.get(url, {'page': 1})
    assert response.status_code == 200

    response = client.get(url, {'page': 656544})
    assert response.status_code == 404


def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200


def test_permissions_not_auth(client):
    urls = (
        'rate:download-csv',
        'rate:download-xlsx',
        'rate:download-json',
    )
    for url in urls:
        response = client.get(reverse(url))
        assert response.status_code == 302


def test_permissions_auth(client, user):
    client.login(username=user.username, password=user.raw_password)
    urls = (
        'rate:download-csv',
        'rate:download-xlsx',
        'rate:download-json',
    )
    for url in urls:
        response = client.get(reverse(url))
        assert response.status_code == 200


def test_rate_download_csv(client, user):
    client.login(username=user.username, password=user.raw_password)
    url = reverse('rate:download-csv')
    response = client.get(url)

    assert response.status_code == 200
    assert response._headers['content-type'] == ('Content-Type', 'text/csv')


def test_rate_download_xlsx(client, user):
    client.login(username=user.username, password=user.raw_password)
    url = reverse('rate:download-xlsx')
    response = client.get(url)
    assert response.status_code == 200
    assert response._headers['content-type'] == (
        'Content-Type',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def test_rate_download_json(client, user):
    client.login(username=user.username, password=user.raw_password)
    url = reverse('rate:download-json')
    response = client.get(url)
    assert response.status_code == 200
    assert response._headers['content-type'] == (
        'Content-Type',
        'application/json'
    )


def test_delete_rate_not_auth(client):
    rate_id = Rate.objects.last().id
    url = reverse('rate:remove', kwargs={'pk': rate_id})
    response = client.get(url)
    assert response.status_code == 404


def test_delete_rate_auth_user(client, user):
    client.login(username=user.username, password=user.raw_password)
    rate_id = Rate.objects.last().id
    url = reverse('rate:remove', kwargs={'pk': rate_id})
    response = client.get(url)
    assert response.status_code == 403


def test_delete_rate_auth_admin(admin_client):
    initial_count = Rate.objects.count()

    # get
    rate_id = Rate.objects.last().id
    url = reverse('rate:remove', kwargs={'pk': rate_id})
    response = admin_client.get(url, follow=True)
    assert response.status_code == 200

    # post(delete)
    response = admin_client.post(url)
    assert response.status_code == 302
    assert Rate.objects.count() == initial_count - 1

    # check success redirect (we have to delete one more, cuz prior doesn't exist)
    rate_id = Rate.objects.last().id
    url = reverse('rate:remove', kwargs={'pk': rate_id})
    assert response['Location'] == reverse('rate:list')
    response = admin_client.post(url, follow=True)
    assert response.status_code == 200


def test_edit_rate_not_auth(client):
    rate_id = Rate.objects.last().id
    url = reverse('rate:edit', kwargs={'pk': rate_id})
    response = client.get(url)
    assert response.status_code == 404


def test_edit_rate_auth_user(client, user):
    client.login(username=user.username, password=user.raw_password)
    rate_id = Rate.objects.last().id
    url = reverse('rate:edit', kwargs={'pk': rate_id})
    response = client.get(url)
    assert response.status_code == 403


def test_edit_rate_auth_admin(admin_client):
    # get
    rate = Rate.objects.last()
    url = reverse('rate:edit', kwargs={'pk': rate.id})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_edit_rate_admin_correct_payload(admin_client):
    rate = Rate.objects.last()
    url = reverse('rate:edit', kwargs={'pk': rate.id})

    payload = {
        'source': 1,
        'currency': 1,
        'buy': to_decimal(23.65),
        'sale': to_decimal(25.50),
        format: 'json'
    }  # test auxiliary funcs, just in case.
    response = admin_client.post(url, payload)
    assert response.status_code == 302
    edited_rate = Rate.objects.filter(id=rate.id).last()
    assert edited_rate.source == payload['source']
    assert edited_rate.currency == payload['currency']
    assert edited_rate.buy == payload['buy']
    assert edited_rate.sale == payload['sale']

    # check success redirect
    assert response['Location'] == reverse('rate:list')
    response = admin_client.post(url, payload, follow=True)
    assert response.status_code == 200


def test_edit_rate_admin_empty_payload(admin_client):
    rate = Rate.objects.last()
    url = reverse('rate:edit', kwargs={'pk': rate.id})
    response = admin_client.post(url, {})
    errors = response.context_data['form'].errors
    assert len(errors) == 4
    fields = ('source', 'currency', 'buy', 'sale')
    for field in fields:
        assert errors[field] == ['This field is required.']


def test_edit_rate_admin_incorrect_payload(admin_client):
    rate = Rate.objects.last()
    url = reverse('rate:edit', kwargs={'pk': rate.id})
    incorrect_data = {
        'source': '322',
        'currency': '228',
        'buy': 'asd',
        'sale': 'zxc',
        format: 'json'
    }
    response = admin_client.post(url, incorrect_data)
    errors = response.context_data['form'].errors
    assert len(errors) == 4
    assert errors['source'] == [
        f'Select a valid choice. {incorrect_data["source"]} is not one of the available choices.'
    ]
    assert errors['currency'] == [
        f'Select a valid choice. {incorrect_data["currency"]} is not one of the available choices.'
    ]
    assert errors['buy'] == ['Enter a number.']
    assert errors['sale'] == ['Enter a number.']


def test_latest_rates(client):
    # get
    url = reverse('rate:rate-latest')
    response = client.get(url)
    assert response.status_code == 200

    # data validation
    db_rates = Rate.objects.all()
    assert len(response.context['object_list']) != 0
    assert len(response.context['object_list']) != len(db_rates)
    assert response.context['object_list'][0] in db_rates
    assert 'USD' in str(response.content)
