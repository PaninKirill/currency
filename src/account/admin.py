from account.models import User

from django.contrib import admin


class AccountAdmin(admin.ModelAdmin):
    list_per_page = 25


admin.site.register(User, AccountAdmin)
