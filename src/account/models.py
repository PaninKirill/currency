from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Contact(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email_from = models.EmailField()
    title = models.CharField(max_length=128)
    message = models.TextField()
