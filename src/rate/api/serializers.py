from rate.models import Rate

from rest_framework import serializers


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = [
            'id',
            'created',
            'buy',
            'sale',
            'source',
            'currency',
        ]
