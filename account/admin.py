from django.contrib import admin

from account import models


class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    search_fields = ['name']


admin.site.register(models.Account, AccountAdmin)
