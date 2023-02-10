from admin_auto_filters.filters import AutocompleteFilterFactory
from django.conf import settings
from django.contrib import admin

from main import models


@admin.register(models.ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_display = ['name', 'category', 'metric', 'metric_name', 'order']
    list_editable = ['order']
    list_filter = [
        AutocompleteFilterFactory('Content Category', 'category'),
    ]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                'difficulty',
                'icon',
            ),
        }),
        ('Options', {
            'fields': (
                'slug',
                ('metric', 'metric_name'),
                ('ordering', 'order'),
            ),
            'classes': (
                'collapse',
            ),
        }),
    )


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['content']
    list_display = ['name', 'content', 'team_size', 'flex_order']
    list_editable = ['flex_order']
    list_filter = [
        AutocompleteFilterFactory('Content Category', 'content__category'),
        AutocompleteFilterFactory('Content', 'content'),
    ]
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'content',
                'team_size',
                'flex_order'
            ),
        }),
    )


@admin.register(models.Pet)
class PetAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.RecordSubmission)
class RecordSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['accounts', 'board']
    list_display = ['accounts_display', 'board', 'value', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Accounts', 'accounts'),
        AutocompleteFilterFactory('Board', 'board'),
    ]
    search_fields = ['accounts__name', 'board__name']

    fieldsets = (
        (None, {
            'fields': (
                'accounts',
                'board',
                'value',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Accounts')
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list('name', flat=True))


@admin.register(models.PetSubmission)
class PetSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'pet']
    list_display = ['account', 'pet', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Account', 'account'),
        AutocompleteFilterFactory('Pet', 'pet'),
    ]
    search_fields = ['account__name', 'pet__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'pet',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )


@admin.register(models.ColLogSubmission)
class ColLogSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account']
    list_display = ['account', 'col_logs_display', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Account', 'account'),
    ]
    search_fields = ['account__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'col_logs',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Collections Logged')
    def col_logs_display(self, obj):
        return f'{obj.col_logs}/{settings.MAX_COL_LOG}'


@admin.register(models.CASubmission)
class CASubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account']
    list_display = ['account', 'ca_tier', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Account', 'account'),
    ]
    search_fields = ['account__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'ca_tier',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )
