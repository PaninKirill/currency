import django_filters
from django_filters.widgets import DateRangeWidget

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
        lookup_expr='date',
        widget=DateRangeWidget(attrs={
            'class': 'form-control datetimepicker-input',
            'type': 'date',
        })
    )

    class Meta:
        model = Rate
        fields = '__all__'
