from django.urls import path, re_path

from rate import views

app_name = 'rate'

urlpatterns = [
    path('list/', views.RatesList.as_view(), name='list'),
    path('rate-latest/', views.LatestRatesView.as_view(), name='rate-latest'),
    re_path(r'^download-csv/(?P<query_params>.*)/$', views.RateDownloadCSV.as_view(), name='download-csv'),
    re_path(r'^download-xlsx/(?P<query_params>.*)/$', views.RateDownloadXLSX.as_view(), name='download-xlsx'),
    re_path(r'^download-json/(?P<query_params>.*)/$', views.RateDownloadJSON.as_view(), name='download-json'),
    path('rate-edit/<int:pk>', views.EditRate.as_view(), name='edit'),
    path('rate-remove/<int:pk>', views.DeleteRate.as_view(), name='remove'),
]
