from account import views

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

app_name = 'account'

urlpatterns = [
    path('contact-us/', views.ContactUs.as_view(), name='contact-us'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my-profile/}', views.MyProfile.as_view(), name='my-profile'),
]
