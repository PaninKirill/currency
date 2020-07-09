from account.models import User
from account.tasks import send_signup_email_async

from django import forms
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with given email exists!')
        return email

    def clean(self):
        cleaned_data = super().clean()  # self.errors
        if not self.errors:
            if cleaned_data['password1'] != cleaned_data['password2']:
                raise forms.ValidationError('Passwords do not match!')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.username = instance.email
        instance.is_active = False
        instance.set_password(self.cleaned_data['password1'])
        instance.save()

        send_signup_email_async(instance.id)
        return instance
