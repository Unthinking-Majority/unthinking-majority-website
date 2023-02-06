from django.contrib import admin

from account import models


class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    search_fields = ['name']
    list_filter = ['active']


admin.site.register(models.Account, AccountAdmin)
