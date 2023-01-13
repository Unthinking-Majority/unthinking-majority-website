from django.contrib import admin

from main import models
from main.admin.autocomplete_filters import AccountsFilter, BoardFilter


class BoardCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ParentBoardAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_display = ['name', 'category', 'metric', 'metric_name']


class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['parent']
    list_display = ['name', 'parent', 'team_size']
    list_filter = ['parent']
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'parent',
                'team_size',
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
admin.site.register(models.ParentBoard, ParentBoardAdmin)
admin.site.register(models.Pet, PetAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
