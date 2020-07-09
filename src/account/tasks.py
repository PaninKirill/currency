from account.tokens import account_activation_token

from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@shared_task
def send_email_async(data: dict):
    send_mail(
        data['title'],
        data['message'],
        data['email_from'],
        [settings.DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )


@shared_task
def send_signup_email_async(user_id):
    from account.models import User

    user = User.objects.get(id=user_id)
    title = 'Sign Up'

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    path = reverse('account:activate', args=(uid, token))
    url = 'http://127.0.0.1:8000' + path

    message = f'Your Activation Url: {url}'
    send_mail(
        title,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
