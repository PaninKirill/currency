from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg
