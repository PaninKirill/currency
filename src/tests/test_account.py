import os

from account.models import Contact, User
from account.tasks import send_signup_email_async

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


def test_sanity():
    assert 200 == 200


def test_contact_us_get_form(client):
    url = reverse('account:contact-us')
    response = client.get(url)
    assert response.status_code == 200


def test_contact_us_empty_payload(client):
    assert len(mail.outbox) == 0
    initial_count = Contact.objects.count()
    url = reverse('account:contact-us')
    response = client.post(url, {})
    assert response.status_code == 200
    errors = response.context_data['form'].errors
    assert len(errors) == 3
    assert errors['email_from'] == ['This field is required.']
    assert errors['title'] == ['This field is required.']
    assert errors['message'] == ['This field is required.']
    assert Contact.objects.count() == initial_count
    assert len(mail.outbox) == 0


def test_contact_us_incorrect_payload(client):
    initial_count = Contact.objects.count()
    assert len(mail.outbox) == 0

    url = reverse('account:contact-us')
    payload = {
        'email_from': 'mailmail',
        'title': 'hello world',
        'message': 'hello world\n' * 50,
    }
    response = client.post(url, payload)
    assert response.status_code == 200
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['email_from'] == ['Enter a valid email address.']
    assert Contact.objects.count() == initial_count
    assert len(mail.outbox) == 0


def test_contact_us_correct_payload(client, settings, fake):
    initial_contact_count = Contact.objects.count()
    initial_mail_count = len(mail.outbox)

    url = reverse('account:contact-us')
    payload = {
        'email_from': fake.email(),
        'title': fake.word(),
        'message': fake.text(),
    }
    response = client.post(url, payload)
    assert response.status_code == 302
    assert Contact.objects.count() == initial_contact_count + 1

    # check email
    assert len(mail.outbox) == initial_mail_count + 1
    email = mail.outbox[initial_mail_count]
    assert email.subject == payload['title']
    assert email.body == payload['message']
    assert email.from_email == payload['email_from']
    assert email.to == [settings.DEFAULT_FROM_EMAIL]


def test_profile_not_auth(client):
    client.logout()
    url = reverse('account:my-profile')
    response = client.get(url)
    assert response.status_code == 302


def test_user_profile_edit_incorrect_payload(client, user):
    client.force_login(user)
    url = reverse('account:my-profile')
    payload = {
        'email': 'asd',
        'first_name': 'hello',
        'last_name': 'world',
    }
    response = client.post(url, payload)
    assert response.status_code == 200
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['email'] == ['Enter a valid email address.']


def test_user_profile_edit_correct_payload(client, user):
    client.force_login(user)
    url = reverse('account:my-profile')
    payload = {
        'email': 'user@mail.com',
        'first_name': 'hello',
        'last_name': 'world',
    }
    response = client.post(url, payload)
    assert response.status_code == 302
    user = User.objects.filter(id=user.id).last()
    assert user.email == payload['email']
    assert user.first_name == payload['first_name']
    assert user.last_name == payload['last_name']


def test_avatar_upload(client, user):
    client.force_login(user)
    url = reverse('account:my-profile')
    path = os.path.join(settings.BASE_DIR, 'tests', 'data_fixtures', 'ava3_6D2R1A5.png')
    avatar = SimpleUploadedFile(path, b'file_content', content_type='image/png')
    response = client.post(url, data={'avatar': avatar})
    assert response.status_code == 302
    assert response['Location'] == reverse('index')


def test_login(client, user):
    url = reverse('account:login')
    response = client.get(url)
    assert response.status_code == 200

    # correct payload
    response = client.post(
        url,
        data={'username': user.username, 'password': user.raw_password, format: 'json'},
    )
    assert user.is_authenticated
    assert response.status_code == 302
    assert response['Location'] == reverse('index')
    response = client.post(url, follow=True)
    assert response.status_code == 200

    # empty payload
    response = client.post(url, {})
    errors = response.context_data['form'].errors
    assert len(errors) == 2
    assert errors['username'] == ['This field is required.']
    assert errors['password'] == ['This field is required.']

    # incorrect payload
    response = client.post(
        url,
        data={'username': 'asddfg', 'password': 'asdxzvc', format: 'json'},
    )
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['__all__'] == [
        'Please enter a correct username and password. Note that both fields may be case-sensitive.'
    ]


def test_logout(client, user):
    client.force_login(user)
    url = reverse('account:logout')

    # check redirect
    response = client.get(url)
    assert response.status_code == 302

    # check success redirect
    assert response['Location'] == reverse('index')
    response = client.get(url, follow=True)
    assert response.status_code == 200


def test_signup_correct_payload(client, fake):
    url = reverse('account:sign-up')
    initial_mail_count = len(mail.outbox)
    response = client.get(url)
    assert response.status_code == 200
    user_email = fake.email()
    user_password = fake.password()
    payload = {
        'email': user_email,
        'password1': user_password,
        'password2': user_password,
    }
    response = client.post(url, payload)
    assert response.status_code == 302
    assert response['Location'] == reverse('index')

    # generate activation url with token
    user = User.objects.last()
    send_signup_email_async(user.id)
    assert len(mail.outbox) == initial_mail_count + 2
    email = mail.outbox[initial_mail_count]
    activation_url = str(email.body).split(' ')[-1]
    token = str(email.body).split('/')[-2]
    uidb64 = str(email.body).split('/')[-3]
    reverse_url = reverse(
        'account:activate',
        kwargs={'uidb64': uidb64, 'token': token}
    )
    assert activation_url.replace(settings.DOMAIN, '') == reverse_url

    # incorrect token
    wrong_url = reverse(
        'account:activate',
        kwargs={'uidb64': uidb64, 'token': '5id-4e247df6037f9cd240fb'}
    )
    response = client.get(settings.DOMAIN + wrong_url)
    assert response.status_code == 200

    # passing activation url
    response = client.get(reverse_url)
    assert response.status_code == 302
    assert response['Location'] == reverse('account:login')

    # new user first login
    payload = {
        'username': user_email,
        'password': user_password,
    }
    response = client.post(response['Location'], payload)
    assert response.status_code == 302
    assert response['Location'] == reverse('index')
    assert user.is_authenticated
    new_user = User.objects.last()
    assert new_user.username == user.username
    assert new_user.is_active


def test_signup_activation_stolen_token(client, settings):
    url = reverse(
        'account:activate',
        kwargs={'uidb64': None, 'token': '5id-4e247df6037f9cd240fb'}
    )
    response = client.post(settings.DOMAIN + url)
    assert response.status_code == 404


def test_signup_incorrect_payload(client, fake):
    url = reverse('account:sign-up')
    response = client.get(url)
    user = User.objects.last()
    assert response.status_code == 200
    payload = {
        'email': user.email,
        'password1': fake.password(),
        'password2': fake.password()
    }
    response = client.post(url, payload)
    errors = response.context_data['form'].errors
    assert len(errors) == 2
    assert errors['email'] == ['User with given email exists!']
    assert errors['password2'] == ["The two password fields didn't match."]

    payload = {
        'email': fake.email(),
        'password1': fake.password(),
        'password2': fake.password(),
    }
    response = client.post(url, payload)
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['password2'] == ["The two password fields didn't match."]


def test_signup_empty_payload(client):
    url = reverse('account:sign-up')
    response = client.get(url)
    assert response.status_code == 200
    payload = None
    response = client.post(url, payload)
    errors = response.context_data['form'].errors
    assert len(errors) == 3
    assert errors['email'] == ['This field is required.']
    assert errors['password1'] == ['This field is required.']
    assert errors['password2'] == ['This field is required.']


def test_password_reset_correct_payload(client):
    url = reverse('password_reset')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'email': 'user@mail.com',
            format: 'json'
        },
    )
    assert response.status_code == 302
    assert response['Location'] == reverse('password_reset_done')
    response = client.post(url, follow=True)
    assert response.status_code == 200


def test_password_reset_incorrect_payload(client):
    url = reverse('password_reset')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'email': '',
            format: 'json'
        },
    )
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['email'] == ['This field is required.']


def test_password_reset_confirm_no_token(client):
    url = 'http://currency-exchange.com/accounts/reset/NTA/no-token/'
    response = client.post(url)
    assert response.status_code == 200
    assert 'Invalid token.' in str(response.content)


def test_password_reset_complete(client):
    url = reverse('password_reset_complete')
    response = client.get(url)
    assert response.status_code == 200


def test_password_change_empty_payload(client, user):
    client.force_login(user)
    url = reverse('password_change')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
            format: 'json'
        },
    )
    errors = response.context_data['form'].errors
    assert len(errors) == 3
    assert errors['old_password'] == ['This field is required.']
    assert errors['new_password1'] == ['This field is required.']
    assert errors['new_password2'] == ['This field is required.']


def test_password_change_incorrect_payload(client, user):
    client.force_login(user)
    url = reverse('password_change')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'old_password': '0',
            'new_password1': 'strongpass',
            'new_password2': 'strongpass',
            format: 'json'
        },
    )
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['old_password'] == ['Your old password was entered incorrectly. Please enter it again.']


def test_password_change_incorrect_payload_short_pass(client, user):
    client.force_login(user)
    url = reverse('password_change')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'old_password': '1234567asd',
            'new_password1': '1',
            'new_password2': '1',
            format: 'json'
        },
    )
    errors = response.context_data['form'].errors
    assert len(errors) == 1
    assert errors['new_password2'] == [
        'This password is too short. '
        'It must contain at least 8 characters.',
        'This password is too common.',
        'This password is entirely numeric.']


def test_password_change_correct_payload(client, user):
    client.force_login(user)
    url = reverse('password_change')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(
        url,
        data={
            'old_password': '1234567asd',
            'new_password1': 'strongpass',
            'new_password2': 'strongpass',
            format: 'json'
        },
    )
    assert response.status_code == 302
    assert response['Location'] == reverse('password_change_done')
    response = client.post(url, follow=True)
    assert response.status_code == 200

    # roll back old pass for other tests
    response = client.post(
        url,
        data={
            'old_password': 'strongpass',
            'new_password1': '1234567asd',
            'new_password2': '1234567asd',
            format: 'json'
        },
    )
    assert response.status_code == 302
    assert response['Location'] == reverse('password_change_done')
    response = client.post(url, follow=True)
    assert response.status_code == 200
