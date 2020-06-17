from account.models import User

from django.test import TestCase
from django.urls import reverse

from rate.models import Rate
from rate.utils import to_decimal


class RateUserTestCase(TestCase):
    fixtures = ["rates.json"]

    def setUp(self):
        client = User.objects.create_user(username='test3', password='test3')
        client.save()
        self.client.login(username='test3', password='test3')

    def test_index_page(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rate_list(self):
        url = reverse('rate:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rate_list_filter_ordering(self):
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
            response = self.client.get(url, {'ordering': param})
            self.assertEqual(response.status_code, 200)

    def test_rate_list_filter_date(self):
        url = reverse('rate:list')
        created_after = '2020-06-08'
        created_before = '2020-06-17'
        response = self.client.get(
            url, {
                'created_after': {created_after},
                'created_before': {created_before}
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_rate_list_filter_source(self):
        url = reverse('rate:list')
        source = 1
        response = self.client.get(url, {'source': {source}})
        self.assertEqual(response.status_code, 200)

    def test_rate_list_filter_currency(self):
        url = reverse('rate:list')
        currency = 2
        response = self.client.get(url, {'currency': {currency}})
        self.assertEqual(response.status_code, 200)

    def test_rate_list_pagination(self):
        url = reverse('rate:list')
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, {'page': 656544})
        self.assertEqual(response.status_code, 404)

    def test_edit_rate_auth_user(self):
        rate = Rate.objects.last()
        url = reverse('rate:edit', kwargs={'pk': rate.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_permissions_auth(self):
        urls = (
            'rate:download-csv',
            'rate:download-xlsx',
            'rate:download-json',
            'rate:api',
        )
        for url in urls:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200)

    def test_rate_download_csv(self):
        url = reverse('rate:download-csv')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        assert response._headers['content-type'] == ('Content-Type', 'text/csv')

    def test_rate_download_xlsx(self):
        url = reverse('rate:download-xlsx')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response._headers['content-type'], (
                'Content-Type',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        )

    def test_rate_download_json(self):
        url = reverse('rate:download-json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response._headers['content-type'],
            ('Content-Type', 'application/json')
        )

    def test_delete_rate_auth_user(self):
        rate_id = Rate.objects.last().id
        url = reverse('rate:remove', kwargs={'pk': rate_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_latest_rates(self):
        # get
        url = reverse('rate:rate-latest')
        response = self.client.get(url)
        assert response.status_code == 200

        # data validation
        db_rates = Rate.objects.all()
        self.assertNotEqual(len(response.context['object_list']), 0)
        self.assertNotEqual(len(response.context['object_list']), len(db_rates))
        self.assertIn(response.context['object_list'][0], db_rates)


class RateNotAuthTestCase(TestCase):
    fixtures = ["rates.json"]

    def test_permissions_not_auth(self):
        urls = (
            'rate:download-csv',
            'rate:download-xlsx',
            'rate:download-json',
            'rate:api',
        )
        for url in urls:
            response = self.client.get(reverse(url))
            assert response.status_code == 302

    def test_delete_rate_not_auth(self):
        rate_id = Rate.objects.last().id
        url = reverse('rate:remove', kwargs={'pk': rate_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_rate_not_auth(self):
        rate_id = Rate.objects.last().id
        url = reverse('rate:edit', kwargs={'pk': rate_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class RateAdminTestCase(TestCase):
    fixtures = ["rates.json"]

    def setUp(self):
        self.login()

    def create_user(self):
        username, password = 'admin', 'test'
        user = User.objects.get_or_create(
            username=username,
            email='admin@test.com',
            is_superuser=True
        )[0]
        user.set_password(password)
        user.save()
        self.user = user
        return username, password

    def login(self):
        username, password = self.create_user()
        self.client.login(username=username, password=password)

    def test_an_admin_view(self):
        response = self.client.get('/admin/')
        assert response.status_code == 302

    def test_delete_rate_auth_admin(self):
        initial_count = Rate.objects.count()

        # get
        rate = Rate.objects.last()
        url = reverse('rate:remove', kwargs={'pk': rate.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        # post(delete)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rate.objects.count(), initial_count - 1)

        # check success redirect (we have to delete one more, cuz prior doesn't exist)
        rate_id = Rate.objects.last().id
        url = reverse('rate:remove', kwargs={'pk': rate_id})
        self.assertEqual(response['Location'], reverse('rate:list'))
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_rate_auth_admin(self):
        # get
        rate = Rate.objects.last()
        url = reverse('rate:edit', kwargs={'pk': rate.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_rate_admin_correct_payload(self):
        rate = Rate.objects.last()
        url = reverse('rate:edit', kwargs={'pk': rate.id})

        payload = {
            'source': 1,
            'currency': 1,
            'buy': to_decimal(23.65),
            'sale': to_decimal(25.50),
            format: 'json'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        edited_rate = Rate.objects.filter(id=rate.id).last()
        self.assertEqual(edited_rate.source, payload['source'])
        self.assertEqual(edited_rate.currency, payload['currency'])
        self.assertEqual(edited_rate.buy, payload['buy'])
        self.assertEqual(edited_rate.sale, payload['sale'])

        # check success redirect
        self.assertEqual(response['Location'], reverse('rate:list'))
        response = self.client.post(url, payload, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_rate_admin_empty_payload(self):
        rate = Rate.objects.last()
        url = reverse('rate:edit', kwargs={'pk': rate.id})
        response = self.client.post(url, {})
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 4)
        fields = ('source', 'currency', 'buy', 'sale')
        for field in fields:
            self.assertEqual(errors[field], ['This field is required.'])

    def test_edit_rate_admin_incorrect_payload(self):
        rate = Rate.objects.last()
        url = reverse('rate:edit', kwargs={'pk': rate.id})
        incorrect_data = {
            'source': '322',
            'currency': '228',
            'buy': 'asd',
            'sale': 'zxc',
            format: 'json'
        }
        response = self.client.post(url, incorrect_data)
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 4)
        self.assertEqual(errors['source'], [
            f'Select a valid choice. {incorrect_data["source"]} is not one of the available choices.'
        ])
        self.assertEqual(errors['currency'], [
            f'Select a valid choice. {incorrect_data["currency"]} is not one of the available choices.'
        ])
        self.assertEqual(errors['buy'], ['Enter a number.'])
        self.assertEqual(errors['sale'], ['Enter a number.'])
