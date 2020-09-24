from datetime import datetime
from decimal import Decimal
from urllib.parse import parse_qsl

from rate.model_choices import BACKGROUND_COLOR_MAPPER as bcm


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


def rate_charts(queryset) -> dict:
    charts_data = {
        'labels': [],
        'datasets': [],
    }

    chart_style = {
        'borderColor': "rgba(75,192,192,1)",
        'borderCapStyle': 'butt',
        'borderDash': [],
        'borderDashOffset': 0.0,
        'borderJoinStyle': 'miter',
        'pointBorderColor': "rgba(75,192,192,1)",
        'pointBackgroundColor': "#fff",
        'pointBorderWidth': 1,
        'pointHoverRadius': 5,
        'pointHoverBackgroundColor': "rgba(75,192,192,1)",
        'pointHoverBorderColor': "rgba(220,220,220,1)",
        'pointHoverBorderWidth': 2,
        'pointRadius': 2,
        'pointHitRadius': 10,
    }

    # Making charts_data['labels'] pattern
    for date in queryset:
        if date.created.strftime("%d.%m.%Y %H:%M") not in charts_data['labels']:
            charts_data['labels'].append(date.created.strftime("%d.%m.%Y %H:%M"))
    expected_data_len = len(charts_data['labels'])

    # Making charts_data['dataset'] pattern
    rate_type = ('buy', 'sale')

    for item in queryset:
        chart_sources = (s['source'] for s in charts_data['datasets'])
        chart_currencies = (c['currency'] for c in charts_data['datasets'])
        if item.get_source_display() not in chart_sources \
                or item.get_currency_display() not in chart_currencies:
            # separate currency type to buy/sale
            for type_ in rate_type:
                charts_data['datasets'].append({
                    'source': item.get_source_display(),
                    'currency': item.get_currency_display(),
                    'rate_type': type_,
                    'label': f'{item.get_source_display()} {item.get_currency_display()}: {type_}',
                    'backgroundColor': [bcm[item.source]],
                    **chart_style,
                    'data': [],
                    'data_tuple': [],
                })

        # fill in charts_data['dataset'] pattern with data (buy, sale)
        for values in charts_data['datasets']:
            rate_date = item.created.strftime("%d.%m.%Y %H:%M")
            for type_ in rate_type:
                if type_ == 'buy':
                    if item.get_source_display() in values['source'] \
                            and item.get_currency_display() in values['currency'] \
                            and type_ in values['rate_type']:
                        values['data_tuple'].append((charts_data['labels'].index(rate_date), str(item.buy)))
                else:
                    if item.get_source_display() in values['source'] \
                            and item.get_currency_display() in values['currency'] \
                            and type_ in values['rate_type']:
                        if not item.sale == 0:
                            values['data_tuple'].append((charts_data['labels'].index(rate_date), str(item.sale)))
    def_value = []
    for dates in charts_data['datasets']:
        data_dict = dict(dates['data_tuple'])
        for i in range(expected_data_len):
            if i in data_dict.keys():
                dates['data'].append(data_dict[i])
                def_value.append(data_dict[i])
            elif len(dates['data_tuple']) == 0:
                dates['data'].append('')
            else:
                dates['data'].append(dates['data_tuple'][0][1])
        # dates['data_tuple'].clear()

    return charts_data
