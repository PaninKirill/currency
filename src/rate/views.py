from urllib.parse import urlencode

from django.http import JsonResponse

from django_filters.views import FilterView

from rate.filters import RateFilter
from rate.models import Rate

from rest_framework.views import APIView


class RateList(FilterView):
    filterset_class = RateFilter
    queryset = Rate.objects.all()
    template_name = 'rate-list.html'
    paginate_by = 15

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
        data = Rate.objects.all().values_list('id', 'created', 'buy', 'sale', 'source', 'currency')
        return JsonResponse({'results': list(data)})
