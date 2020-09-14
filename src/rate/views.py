import csv
import json
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
from rate.utils import display, parse_query_params, rate_charts

from rest_framework.permissions import IsAuthenticated

import xlsxwriter


class FilteredRateList(FilterView):
    filterset_class = RateFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_params = dict(self.request.GET.items())
        if 'page' in query_params:
            query_params.pop('page')
        context['query_params'] = urlencode(query_params)

        charts_data = rate_charts(self.object_list)
        charts_data_json = json.dumps(charts_data, indent=4)
        context['charts_data'] = charts_data_json

        return context


class RatesList(FilteredRateList):
    template_name = 'rate-list.html'

    def get_paginate_by(self, queryset):
        if self.request.user.is_superuser:
            paginate_by = 18
            return paginate_by
        else:
            paginate_by = 20
            return paginate_by


class LatestRatesView(TemplateView):
    template_name = 'rate-latest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest, prior = get_latest_rates()
        rates = zip(latest, prior)
        context['rates'] = rates

        charts_data = rate_charts(latest)
        charts_data_json = json.dumps(charts_data, indent=4)
        context['charts_data'] = charts_data_json

        return context


class RateDownloadCSV(AuthRequiredMixin, View):
    HEADERS = (
        'id',
        'created',
        'buy',
        'sale',
        'source',
        'currency',
    )

    def get(self, request, query_params):
        if not query_params:
            queryset = Rate.objects.all().iterator()
        else:
            filters, ordering = parse_query_params(query_params)
            queryset = Rate.objects.filter(**filters).order_by(ordering)

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


class RateDownloadXLSX(AuthRequiredMixin, View):
    HEADERS = (
        'id',
        'created',
        'buy',
        'sale',
        'source',
        'currency',
    )

    def get(self, request, query_params):
        if not query_params:
            queryset = Rate.objects.all().iterator()
        else:
            filters, ordering = parse_query_params(query_params)
            queryset = Rate.objects.filter(**filters).order_by(ordering)

        output = BytesIO()

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


class RateDownloadJSON(AuthRequiredMixin, View):
    permission_classes = [IsAuthenticated]

    def get(self, request, query_params):
        if not query_params:
            queryset = Rate.objects.all().iterator()
        else:
            filters, ordering = parse_query_params(query_params)
            queryset = Rate.objects.filter(**filters).order_by(ordering)

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
