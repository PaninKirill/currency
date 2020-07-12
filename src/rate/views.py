import csv
from io import BytesIO
from urllib.parse import urlencode

from django.core import serializers
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView, UpdateView, View

from django_filters.views import FilterView

from mixins.mixins import AdminRequiredMixin, AuthRequiredMixin

from rate.filters import RateFilter
from rate.models import Rate
from rate.selectors import get_latest_rates
from rate.serializers import RateSerializer
from rate.utils import display

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

import xlsxwriter


class FilteredRateList(FilterView):  # TODO  implement initial filter params
    filterset_class = RateFilter

    def get_queryset(self, *args, **kwargs):
        queryset = Rate.objects.all().order_by('created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = dict(self.request.GET.items())
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = urlencode(query_params)

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

        background_color_mapper = {
            1: 'rgba(128, 94, 3, 0.2)',
            2: 'rgba(0, 162, 235, 0.2)',
            3: 'rgba(0, 206, 86, 0.2)',
            4: 'rgba(0, 192, 192, 0.2)',
            5: 'rgba(0, 102, 255, 0.2)',
            6: 'rgba(0, 159, 64, 0.2)',
            7: 'rgba(165, 255, 64, 0.2)',
        }

        rate_type = ('buy', 'sale')

        # Making charts data pattern with empty values, but with keys to call in later
        for item in self.object_list:
            chart_sources = [_['source'] for _ in charts_data['datasets']]
            chart_currencies = [_['currency'] for _ in charts_data['datasets']]
            if item.get_source_display() not in chart_sources \
                    or item.get_currency_display() not in chart_currencies:
                # separate currency type to buy/sale
                for type_ in rate_type:
                    charts_data['datasets'].append({
                        'source': item.get_source_display(),
                        'currency': item.get_currency_display(),
                        'rate_type': type_,
                        'label': f'{item.get_source_display()} {item.get_currency_display()}: {type_}',
                        'backgroundColor': [background_color_mapper[item.source]],
                        **chart_style,
                        'data': [],
                    })
            # fill in pattern with data
            for values in charts_data['datasets']:
                for type_ in rate_type:
                    if type_ == 'buy':
                        if item.get_source_display() in values['source'] \
                                and item.get_currency_display() in values['currency'] \
                                and type_ in values['rate_type']:
                            values['data'].append(str(item.buy))
                    else:
                        if item.get_source_display() in values['source'] \
                                and item.get_currency_display() in values['currency'] \
                                and type_ in values['rate_type']:
                            if not item.sale == 0:
                                values['data'].append(str(item.sale))
            charts_data['labels'].append(item.created.strftime("%d.%m.%Y %H:%M"))

        context['charts_data'] = charts_data

        return context


class RatesList(FilteredRateList):
    template_name = 'rate-list.html'
    paginate_by = 25


class ChartData(AuthRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]  # restrictions apply to view data only auth users

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        qs_json = serializers.serialize('json', queryset)
        return HttpResponse(qs_json, content_type='application/json')


class RateListCreateView(AuthRequiredMixin, ListCreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class RateReadUpdateDeleteView(AdminRequiredMixin, RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class LatestRatesView(TemplateView):  # TODO implement indicators to latest update on fields buy/sale (up/down arrows)
    template_name = 'rate-latest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object_list'] = get_latest_rates()

        return context


class RateDownloadCSV(AuthRequiredMixin, View):  # TODO get rid off filtered data
    HEADERS = (
        'id',
        'created',
        'buy',
        'sale',
        'source',
        'currency',
    )

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        response = self.get_response()

        writer = csv.writer(response)
        writer.writerow(self.__class__.HEADERS)

        for rate in queryset:
            values = []
            for attr in self.__class__.HEADERS:
                values.append(display(rate, attr))

            writer.writerow(values)

        return response

    def get_response(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rates.csv"'
        return response


class RateDownloadXLSX(AuthRequiredMixin, View):  # TODO get rid off filtered data
    HEADERS = (
        'id',
        'created',
        'buy',
        'sale',
        'source',
        'currency',
    )

    def get(self, request):
        output = BytesIO()
        queryset = Rate.objects.all().iterator()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("rates")
        columns = self.__class__.HEADERS
        style = workbook.add_format({'bold': True})

        for col, elem in enumerate(columns):  # sheet headers
            worksheet.write(0, col, elem, style)

        for row, rate in enumerate(queryset, start=1):  # sheet rows
            for col, item in enumerate(self.__class__.HEADERS):
                worksheet.write(row, col, display(rate, item))

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="rates.xlsx"'

        return response


class RateDownloadJSON(AuthRequiredMixin, View):  # TODO get rid off filtered data
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        qs_json = serializers.serialize('json', queryset)

        response = HttpResponse(qs_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="rates.json"'

        return response


class DeleteRate(AdminRequiredMixin, DeleteView):
    model = Rate
    template_name = 'rate-delete.html'
    success_url = reverse_lazy('rate:list')


class EditRate(AdminRequiredMixin, UpdateView):
    model = Rate
    template_name = 'rate-edit.html'
    fields = (
        'source',
        'currency',
        'buy',
        'sale',
    )
    success_url = reverse_lazy('rate:list')
