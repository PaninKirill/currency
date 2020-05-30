from django.forms import DateInput

import django_filters

from rate import model_choices as mch
from rate.models import Rate


class RateFilter(django_filters.FilterSet):
    ordering = django_filters.ChoiceFilter(
        label='Ordering',
        choices=mch.FILTER_CHOICES,
        method='filter_by_order',
    )
    created = django_filters.DateFilter(
        field_name='created',
        lookup_expr='date',
        widget=DateInput(attrs={
            'class': 'datepicker',
            'type': 'date',
            'placeholder': 'Select a date',
        })
    )

    class Meta:
        model = Rate
        fields = ['created', 'source', 'currency']

    def filter_by_order(self, queryset, name, value):
        expression = 'created' if value == 'ASC' else '-created'
        return queryset.order_by(expression)
