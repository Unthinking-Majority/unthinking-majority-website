from django.contrib import admin
from django.db.models import When, Case, IntegerField, Value
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from account import models
from dragonstone.models import RecruitmentSubmission, SotMSubmission, PVMSplitSubmission, MentorSubmission, EventSubmission


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['name', 'rank', 'dragonstone_pts', 'is_active']
    list_editable = ['rank']
    list_filter = ['is_active', 'rank']
    search_fields = ['name']
    readonly_fields = [
        'recruitment_submissions',
        'sotm_submissions',
        'pvm_split_submissions',
        'mentor_submissions',
        'event_hosts_submissions',
        'event_participants_submissions',
        'event_donors_submissions',
    ]

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'name',
                'rank',
                'is_active',
                'sotm_submissions',
                'pvm_split_submissions',
                'mentor_submissions',
                'event_hosts_submissions',
                'event_participants_submissions',
                'event_donors_submissions',
            ),
        }),
    )

    def get_queryset(self, request):
        queryset = super(AccountAdmin, self).get_queryset(request)

        recruitment_pts = RecruitmentSubmission.annotate_dragonstone_pts()
        sotm_pts = SotMSubmission.annotate_dragonstone_pts()
        pvm_splits_pts = PVMSplitSubmission.annotate_dragonstone_pts()
        mentor_pts = MentorSubmission.annotate_dragonstone_pts()
        event_pts = EventSubmission.annotate_dragonstone_pts()

        dragonstone_pts = {}
        for obj in recruitment_pts + sotm_pts + pvm_splits_pts + mentor_pts + event_pts:
            if obj['account'] in dragonstone_pts.keys():
                dragonstone_pts[obj['account']] += obj['dragonstone_pts']
            else:
                dragonstone_pts[obj['account']] = obj['dragonstone_pts']

        whens = [When(id=account, then=d_pts) for account, d_pts in dragonstone_pts.items()]
        return queryset.annotate(dragonstone_pts=Case(*whens, output_field=IntegerField(), default=Value(0))).order_by('-dragonstone_pts', 'name')

    @admin.display(description='Dragonstone Points', ordering='dragonstone_pts')
    def dragonstone_pts(self, obj):
        if obj.dragonstone_pts >= 40:
            dragonstone_icon_url = static('img/dragonstone.webp')
            return mark_safe(f'{obj.dragonstone_pts} <img src="{dragonstone_icon_url}" style="height: 30px; width: 30px"/>')
        return obj.dragonstone_pts

    @admin.display(description='Recruitment Submissions')
    def recruitment_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_recruitmentsubmission_changelist')}?{urlencode({'recruiter': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='Skill of the Month Submissions')
    def sotm_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_sotmsubmission_changelist')}?{urlencode({'account': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='PVM Split Submissions')
    def pvm_split_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_pvmsplitsubmission_changelist')}?{urlencode({'accounts': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='Mentor Submissions')
    def mentor_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_mentorsubmission_changelist')}?{urlencode({'mentors': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='Event Hosts Submissions')
    def event_hosts_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'hosts': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='Event Participants Submissions')
    def event_participants_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'participants': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')

    @admin.display(description='Event Donors Submissions')
    def event_donors_submissions(self, obj):
        url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'donors': obj.id})}"
        return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
