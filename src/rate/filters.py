from django import forms

import django_filters
from django_filters.rest_framework import ChoiceFilter, FilterSet
from django_filters.widgets import DateRangeWidget

from rate import model_choices as mch
from rate.models import Rate


class RateFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        label='Ordering',
        choices=(
            ('created', 'Date (ascending)'),
            ('-created', 'Date (descending)'),
            ('sale', 'Currency sale (ascending)'),
            ('-sale', 'Currency sale (descending)'),
            ('buy', 'Currency buy (ascending)'),
            ('-buy', 'Currency buy (descending)'),
        ),
    )
    created = django_filters.DateTimeFromToRangeFilter(
        label='Date range',
        field_name='created',
        lookup_expr='range',
        widget=DateRangeWidget(attrs={
            'class': 'form-control datetimepicker-input',
            'type': 'date',
        })
    )

    class Meta:
        model = Rate
        fields = '__all__'


class RateFilterAPI(RateFilter, FilterSet):
    source = ChoiceFilter(choices=mch.SOURCE_CHOICES)
    currency = ChoiceFilter(choices=mch.CURRENCY_CHOICES)

    filter_choices = [
        ('exact', 'Equals'),
        ('gt', 'Greater than'),
        ('gte', 'Greater than equals'),
        ('lt', 'Less than'),
        ('lte', 'Less than equals'),
    ]

    buy = django_filters.LookupChoiceFilter(
        field_class=forms.DecimalField,
        lookup_choices=filter_choices,
    )

    sale = django_filters.LookupChoiceFilter(
        field_class=forms.DecimalField,
        lookup_choices=filter_choices,
    )

    class Meta:
        model = Rate
        fields = [
            'id',
            'buy',
            'sale',
        ]
