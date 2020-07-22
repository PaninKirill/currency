from django_filters import rest_framework as filters

from rate.api.serializers import RateSerializer
from rate.filters import RateFilterAPI
from rate.models import Rate
from rate.selectors import get_latest_rates
from rate.utils import list_to_queryset

from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication


class RateListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    autentication_classes = [JWTAuthentication]

    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RateFilterAPI


class RateReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    autentication_classes = [JWTAuthentication]

    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class LatestRatesListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    autentication_classes = [JWTAuthentication]

    queryset = list_to_queryset(Rate, get_latest_rates())
    serializer_class = RateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RateFilterAPI
