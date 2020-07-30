from account.models import User
from account.tasks import send_signup_email_async

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        field_classes = {'email': EmailField}

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with given email exists!')
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.username = instance.email
        instance.is_active = False
        instance.set_password(self.cleaned_data['password1'])
        instance.save()

        send_signup_email_async(instance.id)
        return instance
