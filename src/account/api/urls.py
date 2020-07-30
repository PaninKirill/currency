from account.api import views

from django.urls import path

app_name = 'api-account'

urlpatterns = [
    path('users/', views.UserListCreateView.as_view(), name='users'),
    path('users/<int:pk>/', views.UserReadUpdateDeleteView.as_view(), name='user'),

    path('contact/', views.ContactCreateView.as_view(), name='contact'),
]
