import csv
from io import BytesIO
from urllib.parse import urlencode

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.generic import TemplateView, View

from django_filters.views import FilterView

from rate import model_choices as mch
from rate.filters import RateFilter
from rate.models import Rate
from rate.utils import display

from rest_framework.views import APIView

import xlsxwriter


class RateList(FilterView):
    filterset_class = RateFilter
    queryset = Rate.objects.all()
    template_name = 'rate-list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = RateFilter(self.request.GET, queryset=self.queryset)

        query_params = dict(self.request.GET.items())
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = urlencode(query_params)

        return context


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        qs_json = serializers.serialize('json', queryset)
        return HttpResponse(qs_json, content_type='application/json')


class LatestRatesView(TemplateView):
    filterset_class = RateFilter
    template_name = 'rate-latest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = []

        for source in mch.SOURCE_CHOICES:  # source
            source = source[0]
            for currency in mch.CURRENCY_CHOICES:  # currency
                try:
                    currency = currency[0]
                    rate = Rate.objects.filter(
                        source=source,
                        currency=currency,
                    ).latest()
                except ObjectDoesNotExist:
                    continue
                if rate is not None:
                    object_list.append(rate)

        context['object_list'] = object_list

        return context


class RateDownloadCSV(View):
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


class RateDownloadXLSX(View):
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


class RateDownloadJSON(View):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        qs_json = serializers.serialize('json', queryset)

        response = HttpResponse(qs_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="rates.json"'

        return response
