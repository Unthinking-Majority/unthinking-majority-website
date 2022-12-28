from django.contrib import admin

from account import models
from main.admin.autocomplete_filters import AccountFilter, PetFilter


class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    search_fields = ['name']


admin.site.register(models.Account, AccountAdmin)
