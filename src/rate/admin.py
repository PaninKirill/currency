from django.contrib import admin

from rate.models import Rate


class RateAdmin(admin.ModelAdmin):
    list_per_page = 25


admin.site.register(Rate, RateAdmin)
