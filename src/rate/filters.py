import django_filters
from django_filters.widgets import RangeWidget

from rate import model_choices as mch
from rate.models import Rate


class RateFilter(django_filters.FilterSet):
    ordering = django_filters.ChoiceFilter(
        label='Ordering',
        choices=mch.FILTER_CHOICES,
        method='filter_by_order',
    )
    created = django_filters.DateTimeFromToRangeFilter(
        field_name='created',
        lookup_expr='date',
        widget=RangeWidget(attrs={
            'class': 'datepicker',
            'type': 'date',
        })
    )

    class Meta:
        model = Rate
        fields = ['ordering', 'source', 'currency', 'created']

    def filter_by_order(self, queryset, name, value):
        expression = 'created' if value == 'ASC' else '-created'
        return queryset.order_by(expression)
