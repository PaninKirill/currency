from account.models import Contact, User
from account.tasks import send_email_async

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'date_joined',
            'avatar',
        ]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'created',
            'email_from',
            'title',
            'message',
        ]

    def create(self, validated_data):
        obj = super().create(validated_data)
        send_email_async.delay(validated_data)
        return obj
