from django.urls import path

from account import views

app_name = 'account'

urlpatterns = [
    path('index/', views.index, name='index'),
]
