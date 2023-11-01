from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from dragonstone import models


@admin.register(models.DragonstoneBaseSubmission)
class DragonstoneBaseSubmissionAdmin(PolymorphicParentModelAdmin):
    base_model = models.DragonstoneBaseSubmission
    child_models = (
        models.FreeformSubmission,
        models.RecruitmentSubmission,
        models.SotMSubmission,
        models.PVMSplitSubmission,
        models.MentorSubmission,
        models.EventSubmission,
    )
    list_display = [
        "_value_display",
        "_accounts_display",
        "proof",
        "date",
        "accepted",
        "_accepted_display",
    ]
    list_editable = ["accepted"]
    list_filter = ["accepted", "date", PolymorphicChildModelFilter]

    @admin.display(description="Account(s)")
    def _accounts_display(self, obj):
        return obj.accounts_display()

    @admin.display(description="Type")
    def _value_display(self, obj):
        return obj.type_display()

    @admin.display(description="", ordering="accepted", boolean=True)
    def _accepted_display(self, obj):
        return obj.accepted


class DragonstoneBaseSubmissionChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.DragonstoneBaseSubmission


@admin.register(models.FreeformSubmission)
class FreeformSubmission(PolymorphicChildModelAdmin):
    base_model = models.FreeformSubmission
    autocomplete_fields = ["account"]
    list_display = ["account", "dragonstone_pts", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        AutocompleteFilterFactory("Created by", "created_by"),
    ]
    readonly_fields = ["created_by"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "dragonstone_pts",
                    "created_by",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()


@admin.register(models.RecruitmentSubmission)
class RecruitmentAdmin(PolymorphicChildModelAdmin):
    base_model = models.RecruitmentSubmission
    autocomplete_fields = ["recruiter", "recruited"]
    list_display = ["recruiter", "recruited", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Recruiter", "recruiter"),
        AutocompleteFilterFactory("Recruited", "recruited"),
        "accepted",
        "date",
    ]
    search_fields = ["recruiter__name", "recruited__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "recruiter",
                    "recruited",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )


@admin.register(models.SotMSubmission)
class SotMAdmin(PolymorphicChildModelAdmin):
    base_model = models.SotMSubmission
    autocomplete_fields = ["account"]
    list_display = ["account", "rank_display", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        "rank",
        "accepted",
        "date",
    ]
    search_fields = ["account__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "rank",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    @admin.display(description="Rank")
    def rank_display(self, obj):
        return obj.get_rank_display()


@admin.register(models.PVMSplitSubmission)
class PVMSplitAdmin(PolymorphicChildModelAdmin):
    base_model = models.PVMSplitSubmission
    autocomplete_fields = ["content"]
    list_display = ["accounts_display", "content", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Accounts", "accounts"),
        AutocompleteFilterFactory("Content", "content"),
        "content__difficulty",
        "accepted",
        "date",
    ]
    search_fields = ["accounts__name", "content__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "content",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    @admin.display(description="Accounts")
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list("name", flat=True))


@admin.register(models.MentorSubmission)
class MentorAdmin(PolymorphicChildModelAdmin):
    base_model = models.MentorSubmission
    autocomplete_fields = ["learners", "content"]
    list_display = ["mentors_display", "content", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Mentors", "mentors"),
        AutocompleteFilterFactory("Learners", "learners"),
        AutocompleteFilterFactory("Content", "content"),
        "accepted",
        "date",
    ]
    search_fields = ["mentors__name", "learners__name", "content__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "learners",
                    "content",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    @admin.display(description="Mentors")
    def mentors_display(self, obj):
        return ", ".join(obj.mentors.values_list("name", flat=True))


@admin.register(models.EventSubmission)
class EventAdmin(PolymorphicChildModelAdmin):
    base_model = models.EventSubmission
    # autocomplete_fields = ["hosts", "participants", "donors"]
    list_display = ["name", "hosts_display", "type", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Hosts", "hosts"),
        AutocompleteFilterFactory("Participants", "participants"),
        AutocompleteFilterFactory("Donors", "donors"),
        "type",
        "accepted",
        "date",
    ]
    search_fields = ["name", "hosts__name", "participants__name", "donors__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "type",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    @admin.display(description="Hosts")
    def hosts_display(self, obj):
        return ", ".join(obj.hosts.values_list("name", flat=True))


# @admin.register(models.DragonstonePoints)
# class DragonstonePointsAdmin(admin.ModelAdmin):
#     model = models.DragonstonePoints
#     autocomplete_fields = ["account"]
#     raw_id_fields = ["submission"]
