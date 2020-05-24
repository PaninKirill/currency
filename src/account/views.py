from django.http import HttpResponse
from django.shortcuts import render  # NOQA


def index(request):
    return HttpResponse('Hello from account')
