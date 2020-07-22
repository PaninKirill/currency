from django.urls import path

from rate.api import views

app_name = 'api-rate'

urlpatterns = [
    path('rates/', views.RateListCreateView.as_view(), name='rates'),
    path('latest-rates/', views.LatestRatesListView.as_view(), name='latest_rates'),
    path('rates/<int:pk>/', views.RateReadUpdateDeleteView.as_view(), name='rate'),
]
