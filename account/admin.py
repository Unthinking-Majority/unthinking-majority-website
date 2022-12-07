from django.contrib import admin

from account import models
from main.autocomplete_filters import AccountFilter, PetFilter


class AccountAdmin(admin.ModelAdmin):
    search_fields = ['name']


class PetOwnershipAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'pet']
    list_display = ['account_name', 'pet_name', 'date']
    list_filter = [AccountFilter, PetFilter, 'date']
    readonly_fields = ['account_name', 'pet_name', 'date']
    search_fields = ['account__name', 'pet__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'pet',
                ('proof', 'date'),
            )
        }),
    )

    def account_name(self, obj):
        return obj.account.name

    def pet_name(self, obj):
        return obj.pet.name


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.PetOwnership, PetOwnershipAdmin)
