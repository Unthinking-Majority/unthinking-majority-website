from django.contrib import admin
from django.db.models import F, Case, When, Sum, Q
from django.db.models import IntegerField, Value
from django.db.models.lookups import GreaterThanOrEqual
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from account import models
from dragonstone import PVM_SPLIT
from dragonstone.models import DragonstonePoints
from main.models import Settings


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "rank", "dragonstone_pts", "is_active"]
    list_editable = ["rank"]
    list_filter = ["is_active", "rank"]
    search_fields = ["name"]
    readonly_fields = [
        "recruitment_submissions",
        "sotm_submissions",
        "pvm_split_submissions",
        "mentor_submissions",
        "event_hosts_submissions",
        "event_participants_submissions",
        "event_donors_submissions",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "preferred_name"),
                    "rank",
                    ("is_active", "is_alt"),
                    "sotm_submissions",
                    "pvm_split_submissions",
                    "mentor_submissions",
                    "event_hosts_submissions",
                    "event_participants_submissions",
                    "event_donors_submissions",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super(AccountAdmin, self).get_queryset(request)

        dstone_pts = (
            DragonstonePoints.objects.filter(
                submission__accepted=True,
                submission__date__gte=DragonstonePoints.expiration_period(),
            )
            .values("account", "type")
            .annotate(pts=Sum("points"))
            .annotate(
                pts=Case(
                    When(
                        Q(type=PVM_SPLIT) & Q(GreaterThanOrEqual(F("pts"), 25)),
                        then=25,
                    ),
                    default=F("pts"),
                    output_field=IntegerField(),
                )
            )
            .order_by()
        )

        foo = {}
        for obj in dstone_pts:
            if obj["account"] not in foo.keys():
                foo[obj["account"]] = obj["pts"]
            else:
                foo[obj["account"]] += obj["pts"]

        whens = [When(id=account, then=pts) for account, pts in foo.items()]
        return queryset.annotate(
            dragonstone_pts=Case(*whens, output_field=IntegerField(), default=Value(0))
        ).order_by("-dragonstone_pts", "name")

    @admin.display(description="Dragonstone Points", ordering="dragonstone_pts")
    def dragonstone_pts(self, obj):
        if obj.dragonstone_pts >= int(
            Settings.objects.get(name="DRAGONSTONE_POINTS_THRESHOLD").value
        ):
            dragonstone_icon_url = static("dragonstone/img/dragonstone.webp")
            return mark_safe(
                f'{obj.dragonstone_pts} <img src="{dragonstone_icon_url}" style="height: 17px; width: 17px"/>'
            )
        return obj.dragonstone_pts

    @admin.display(description="Recruitment Submissions")
    def recruitment_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_recruitmentsubmission_changelist')}?{urlencode({'recruiter': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="Skill of the Month Submissions")
    def sotm_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_sotmsubmission_changelist')}?{urlencode({'account': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="PVM Split Submissions")
    def pvm_split_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_pvmsplitsubmission_changelist')}?{urlencode({'accounts': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="Mentor Submissions")
    def mentor_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_mentorsubmission_changelist')}?{urlencode({'mentors': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="Event Hosts Submissions")
    def event_hosts_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'hosts': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="Event Participants Submissions")
    def event_participants_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'participants': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"

    @admin.display(description="Event Donors Submissions")
    def event_donors_submissions(self, obj):
        if obj.id:
            url = f"{reverse_lazy(f'admin:dragonstone_eventsubmission_changelist')}?{urlencode({'donors': obj.id})}"
            return mark_safe(f'<a target="_blank" href={url}>Click Here</a>')
        else:
            return "-"


@admin.register(models.UserCreationSubmission)
class UserCreationSubmissionAdmin(admin.ModelAdmin):
    list_display = ["username", "account", "phrase", "proof", "accepted"]
    list_editable = ["accepted"]
    list_filter = ["accepted"]
    readonly_fields = ["username", "account", "phrase"]
    fieldsets = (
        (
            None,
            {
                "fields": ("username", "account", ("proof", "phrase"), "accepted"),
            },
        ),
    )
