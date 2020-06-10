from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def active(path, url_name):
    if path == reverse(url_name):
        return 'active'
    return ''
