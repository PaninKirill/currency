from account.models import Contact, User

from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class TestSanity(TestCase):

    def test_sanity(self):
        self.assertEqual(200, 200)


class AccountUserTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='test3', password='test3')
        test_user.save()
        self.client.login(username='test3', password='test3')

    def test_login(self):
        url = reverse('account:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {})
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors['username'], ['This field is required.'])
        self.assertEqual(errors['password'], ['This field is required.'])

        # incorrect payload
        response = self.client.post(
            url,
            data={'username': 'asddfg', 'password': 'asdxzvc', format: 'json'},
        )
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors['__all__'],
            [
                'Please enter a correct username and password. Note that both fields may be case-sensitive.'
            ]
        )

    def test_logout(self):
        url = reverse('account:logout')

        # check redirect
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # check success redirect
        self.assertEqual(response['Location'], reverse('index'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_edit_correct_payload(self):
        url = reverse('account:my-profile')
        payload = {
            'email': 'user@mail.com',
            'first_name': 'hello',
            'last_name': 'world',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username='test3').last()
        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.first_name, payload['first_name'])
        self.assertEqual(user.last_name, payload['last_name'])

    def test_user_profile_edit_incorrect_payload(self):
        url = reverse('account:my-profile')
        payload = {
            'email': 'asd',
            'first_name': 'hello',
            'last_name': 'world',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors['email'], ['Enter a valid email address.'])

    def test_contact_us_correct_payload(self):
        initial_count = Contact.objects.count()
        self.assertEqual(len(mail.outbox), 0)

        url = reverse('account:contact-us')
        payload = {
            'email_from': 'mailmail@mail.com',
            'title': 'hello world',
            'message': 'hello world' * 50,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contact.objects.count(), initial_count + 1)

        # check email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, payload['title'])
        self.assertEqual(email.body, payload['message'])
        self.assertEqual(email.from_email, payload['email_from'])
        self.assertEqual(email.to, [settings.DEFAULT_FROM_EMAIL])

    def test_contact_us_empty_payload(self):
        self.assertEqual(len(mail.outbox), 0)
        initial_count = Contact.objects.count()
        url = reverse('account:contact-us')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 3)
        self.assertEqual(errors['email_from'], ['This field is required.'])
        self.assertEqual(errors['title'], ['This field is required.'])
        self.assertEqual(errors['message'], ['This field is required.'])
        self.assertEqual(Contact.objects.count(), initial_count)
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_us_incorrect_payload(self):
        initial_count = Contact.objects.count()
        self.assertEqual(len(mail.outbox), 0)

        url = reverse('account:contact-us')
        payload = {
            'email_from': 'mailmail',
            'title': 'hello world',
            'message': 'hello world\n' * 50,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        errors = response.context_data['form'].errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors['email_from'], ['Enter a valid email address.'])
        self.assertEqual(Contact.objects.count(), initial_count)
        self.assertEqual(len(mail.outbox), 0)


class AccountNotAuthTestCase(TestCase):

    def test_contact_us_get_form(self):
        url = reverse('account:contact-us')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_not_auth(self):
        url = reverse('account:my-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
