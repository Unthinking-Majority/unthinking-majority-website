from django.contrib import admin

from account import models


class AccountAdmin(admin.ModelAdmin):
    pass


class PetOwnershipAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.PetOwnership, PetOwnershipAdmin)
