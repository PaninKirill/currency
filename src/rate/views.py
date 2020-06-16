import csv
from io import BytesIO
from urllib.parse import urlencode

from django.core import serializers
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView, UpdateView, View

from django_filters.views import FilterView

from rate.filters import RateFilter
from rate.mixins import AdminRequiredMixin, AuthRequiredMixin
from rate.models import Rate
from rate.selectors import get_latest_rates
from rate.utils import display

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

import xlsxwriter


class FilteredRateList(FilterView):  # TODO  implement initial filter params
    filterset_class = RateFilter

    def get_queryset(self, *args, **kwargs):
        queryset = Rate.objects.all().order_by('-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = RateFilter(self.request.GET, queryset=self.get_queryset())

        query_params = dict(self.request.GET.items())
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = urlencode(query_params)

        return context


class RatesList(FilteredRateList):
    template_name = 'rate-list.html'
    paginate_by = 25


class ChartData(APIView):
    permission_classes = [IsAuthenticated]  # restrictions apply to view data only auth users

    def get(self, request):
        queryset = Rate.objects.all().iterator()
        qs_json = serializers.serialize('json', queryset)
        return HttpResponse(qs_json, content_type='application/json')


class LatestRatesView(AuthRequiredMixin,
                      TemplateView):  # TODO implement indicators to latest update on fields buy/sale (up/down arrows)
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
