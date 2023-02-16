from django.contrib import admin
from django.db.models import When, Case, IntegerField, Value

from account import models
from dragonstone.models import RecruitmentSubmission, SotMSubmission, PVMSplitSubmission, MentorSubmission, EventSubmission


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['name', 'rank', 'dragonstone_pts', 'is_active']
    list_editable = ['rank']
    list_filter = ['is_active', 'rank']
    search_fields = ['name']

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
        return obj.dragonstone_pts
