from django.contrib import admin

from main import models
from main.autocomplete_filters import AccountFilter, BoardCategoryFilter


class BoardCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    list_display = ['name', 'category', 'type', 'metric']
    list_filter = [BoardCategoryFilter, 'type', 'metric']
    prepopulated_fields = {'slug': ('name',), 'metric_name': ('metric',)}
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                ('type', 'metric'),
                'icon',
                'slug',
            )
        }),
    )


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'board']
    list_display = ['account_name', 'board', 'value', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [AccountFilter, 'board', 'date', 'accepted']
    readonly_fields = ['account_name', 'date']
    search_fields = ['account__name', 'value']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                ('board', 'value'),
                ('proof', 'date'),
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
