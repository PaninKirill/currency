from account.models import Contact, User

from django.core import mail
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


def test_contact_us_correct_payload(client, settings):
    initial_count = Contact.objects.count()
    assert len(mail.outbox) == 0

    url = reverse('account:contact-us')
    payload = {
        'email_from': 'mailmail@mail.com',
        'title': 'hello world',
        'message': 'hello world' * 50,
    }
    response = client.post(url, payload)
    assert response.status_code == 302
    assert Contact.objects.count() == initial_count + 1

    # check email
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
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
