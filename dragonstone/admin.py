from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from dragonstone import models


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


class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ['hosts', 'participants', 'donators']
    list_display = ['hosts_display', 'type', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Hosts', 'hosts'),
        AutocompleteFilterFactory('Participants', 'participants'),
        AutocompleteFilterFactory('Donators', 'donators'),
        'type'
    ]
    search_fields = ['hosts__name', 'participants__name', 'donators__name']

    fieldsets = (
        (None, {
            'fields': (
                'hosts',
                'participants',
                'donators',
                'type',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Hosts')
    def hosts_display(self, obj):
        return ", ".join(obj.hosts.values_list('name', flat=True))


admin.site.register(models.RecruitmentSubmission, RecruitmentAdmin)
admin.site.register(models.SotMSubmission, SotMAdmin)
admin.site.register(models.PVMSplitSubmission, PVMSplitAdmin)
admin.site.register(models.MentorSubmission, MentorAdmin)
admin.site.register(models.EventSubmission, EventAdmin)
