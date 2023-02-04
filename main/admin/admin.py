from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from main import models
from main.admin.autocomplete_filters import AccountsFilter, BoardFilter, ContentFilter


class BoardCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ContentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_display = ['name', 'category', 'metric', 'metric_name', 'order']
    list_editable = ['order']
    list_filter = [
        AutocompleteFilterFactory('Board Category', 'category'),
    ]


class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['parent']
    list_display = ['name', 'parent', 'team_size', 'flex_order']
    list_editable = ['flex_order']
    list_filter = [
        AutocompleteFilterFactory('Board Category', 'parent__category'),
        ContentFilter,
    ]
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'parent',
                'team_size',
                'flex_order'
            )
        }),
    )


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['accounts', 'board', 'pet']
    list_display = ['account_names', 'type', 'board', 'value_display', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = ['type', AccountsFilter, BoardFilter, 'date', 'accepted']
    readonly_fields = ['account_names']
    search_fields = ['accounts__name', 'value']

    fieldsets = (
        (None, {
            'fields': (
                ('accounts', 'accepted'),
                'type',
                ('board', 'value'),
                'pet',
                'ca_tier',
                'notes',
                ('proof', 'date'),
            )
        }),
    )

    def account_names(self, obj):
        return ', '.join([account.name for account in obj.accounts.all()])

    account_names.__name__ = 'Accounts'


class PetAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardCategory, BoardCategoryAdmin)
admin.site.register(models.Content, ContentAdmin)
admin.site.register(models.Pet, PetAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
