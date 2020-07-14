from account.models import User

from django_filters import BaseInFilter, BooleanFilter, DateTimeFromToRangeFilter
from django_filters.rest_framework import FilterSet
from django_filters.widgets import DateRangeWidget


class UserFilterAPI(FilterSet):
    date_joined = DateTimeFromToRangeFilter(
        label='Date joined range',
        field_name='created',
        lookup_expr='date',
        widget=DateRangeWidget(attrs={
            'class': 'form-control datetimepicker-input',
            'type': 'date',
        })
    )
    is_active = BooleanFilter()
    user_id = BaseInFilter(field_name='id', label='User id')

    class Meta:
        model = User
        fields = {
            'email': ['icontains'],
            'first_name': ['icontains'],
            'last_name': ['icontains'],
        }
