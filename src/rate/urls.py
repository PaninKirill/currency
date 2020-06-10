from django.urls import path

from rate import views

app_name = 'rate'

urlpatterns = [
    path('list/', views.RatesList.as_view(), name='list'),
    path('api/', views.ChartData.as_view(), name='api'),
    path('rate-latest/', views.LatestRatesView.as_view(), name='rate-latest'),
    path('download-csv/', views.RateDownloadCSV.as_view(), name='download-csv'),
    path('download-xlsx/', views.RateDownloadXLSX.as_view(), name='download-xlsx'),
    path('download-json/', views.RateDownloadJSON.as_view(), name='download-json'),
    path('rate-edit/<int:pk>', views.EditRate.as_view(), name='edit'),
    path('rate-remove/<int:pk>', views.DeleteRate.as_view(), name='remove'),
]
