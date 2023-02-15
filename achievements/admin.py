from admin_auto_filters.filters import AutocompleteFilterFactory
from django.conf import settings
from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from achievements import models


@admin.register(models.BaseSubmission)
class BaseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['accounts', 'child_admin', 'value_display', 'date', 'child_admin', 'accepted']
    list_editable = ['accepted']

    @admin.display(description='Account(s)')
    def accounts(self, obj):
        child_instance = obj.get_child_instance()
        if child_instance.__class__ is models.RecordSubmission:
            return ', '.join(child_instance.accounts.values_list('name', flat=True))
        else:
            return child_instance.account.name

    @admin.display(description='Child Admin')
    def child_admin(self, obj):
        url = reverse_lazy(f'admin:achievements_{obj.get_child_instance()._meta.model_name}_change', kwargs={'object_id': obj.id})
        return mark_safe(f'<a target="_blank" href={url}>{obj.type_display()} ({obj.id})</a>')


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
