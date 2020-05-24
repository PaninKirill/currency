from account import views

from django.urls import path

app_name = 'account'

urlpatterns = [
    path('index/', views.index, name='index'),
]
