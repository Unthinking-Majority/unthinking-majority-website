from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from dragonstone import models


@admin.register(models.DragonstoneBaseSubmission)
class DragonstoneBaseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['accounts', 'child_admin', 'value_display', 'date', 'child_admin', 'accepted']
    list_editable = ['accepted']

    @admin.display(description='Account(s)')
    def accounts(self, obj):
        child_instance = obj.get_child_instance()
        if child_instance.__class__ is models.PVMSplitSubmission:
            return ', '.join(child_instance.accounts.values_list('name', flat=True))
        elif child_instance.__class__ is models.MentorSubmission:
            return ', '.join(child_instance.mentors.values_list('name', flat=True))
        elif child_instance.__class__ is models.EventSubmission:
            return ', '.join(child_instance.hosts.values_list('name', flat=True))
        else:
            return child_instance.account.name

    @admin.display(description='Child Admin')
    def child_admin(self, obj):
        url = reverse_lazy(f'admin:dragonstone_{obj.get_child_instance()._meta.model_name}_change', kwargs={'object_id': obj.id})
        return mark_safe(f'<a target="_blank" href={url}>{obj.type_display()} ({obj.id})</a>')


@admin.register(models.RecruitmentSubmission)
class RecruitmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['recruiter', 'recruited']
    list_display = ['recruiter', 'recruited', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Recruiter', 'recruiter'),
        AutocompleteFilterFactory('Recruited', 'recruited'),
    ]
    search_fields = ['recruiter__name', 'recruited__name']

    fieldsets = (
        (None, {
            'fields': (
                'recruiter',
                'recruited',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )


@admin.register(models.SotMSubmission)
class SotMAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account']
    list_display = ['account', 'rank_display', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Account', 'account'),
    ]
    search_fields = ['account__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'rank',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Rank')
    def rank_display(self, obj):
        nth = {
            1: '1st',
            2: '2nd',
            3: '3rd'
        }
        return nth[obj.rank]


@admin.register(models.PVMSplitSubmission)
class PVMSplitAdmin(admin.ModelAdmin):
    autocomplete_fields = ['accounts', 'content']
    list_display = ['accounts_display', 'content', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Accounts', 'accounts'),
        AutocompleteFilterFactory('Content', 'content'),
    ]
    search_fields = ['accounts__name', 'content__name']

    fieldsets = (
        (None, {
            'fields': (
                'accounts',
                'content',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Accounts')
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list('name', flat=True))


@admin.register(models.MentorSubmission)
class MentorAdmin(admin.ModelAdmin):
    autocomplete_fields = ['mentors', 'learners', 'content']
    list_display = ['mentors_display', 'content', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Mentors', 'mentors'),
        AutocompleteFilterFactory('Learners', 'learners'),
        AutocompleteFilterFactory('Content', 'content'),
    ]
    search_fields = ['mentors__name', 'learners__name', 'content__name']

    fieldsets = (
        (None, {
            'fields': (
                'mentors',
                'learners',
                'content',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Mentors')
    def mentors_display(self, obj):
        return ", ".join(obj.mentors.values_list('name', flat=True))


@admin.register(models.EventSubmission)
class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ['hosts', 'participants', 'donors']
    list_display = ['hosts_display', 'type', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Hosts', 'hosts'),
        AutocompleteFilterFactory('Participants', 'participants'),
        AutocompleteFilterFactory('Donors', 'donors'),
        'type'
    ]
    search_fields = ['hosts__name', 'participants__name', 'donors__name']

    fieldsets = (
        (None, {
            'fields': (
                'hosts',
                'participants',
                'donors',
                'type',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Hosts')
    def hosts_display(self, obj):
        return ", ".join(obj.hosts.values_list('name', flat=True))
