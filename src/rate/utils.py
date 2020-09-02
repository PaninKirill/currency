from datetime import datetime
from decimal import Decimal
from urllib.parse import parse_qsl


def to_decimal(num) -> Decimal:
    return round(Decimal(num), 2)


def display(model_object, attr):
    display_attr = f'get_{attr}_display'

    if hasattr(model_object, display_attr):
        return getattr(model_object, display_attr)()

    if type(getattr(model_object, attr)) is datetime:
        return model_object.datetime_str()

    return getattr(model_object, attr)


def list_to_queryset(model, data):
    pk_list = [obj.pk for obj in data]

    return model.objects.filter(pk__in=pk_list)


def parse_query_params(query_params):
    filter_params = parse_qsl(query_params)
    filters = dict(filter_params)
    if 'created_after' in filters.keys():
        filters['created__gte'] = filters.pop('created_after')
    if 'created_before' in filters.keys():
        filters['created__lte'] = filters.pop('created_before')
    if 'ordering' in filters.keys():
        ordering = filters.pop('ordering')
    else:
        ordering = '-created'

    return filters, ordering
