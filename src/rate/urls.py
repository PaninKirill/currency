from django.urls import path

from rate import views

app_name = 'rate'

urlpatterns = [
    path('list/', views.RateList.as_view(), name='list'),
    path('api/', views.ChartData.as_view()),
]
