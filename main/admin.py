from django.contrib import admin

from main import models
from main.autcomplete_filters import AccountFilter


class BoardCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


class BoardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'board']
    list_display = ['account_name', 'board', 'value', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [AccountFilter, 'board', 'date', 'accepted']
    readonly_fields = ['account_name']
    search_fields = ['account__name', 'value']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                ('board', 'value'),
                'proof',
                'accepted',
            )
        }),
    )

    def account_name(self, obj):
        return obj.account.name


class PetAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardCategory, BoardCategoryAdmin)
admin.site.register(models.Pet, PetAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
