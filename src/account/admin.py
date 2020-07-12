from account.models import User

from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    fields = ['email', 'first_name', 'last_name', 'avatar']


admin.site.register(User, UserAdmin)
