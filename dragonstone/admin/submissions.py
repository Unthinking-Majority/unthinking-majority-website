from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicInlineSupportMixin,
)

from dragonstone import models
from dragonstone.admin import inlines

__all__ = [
    "DragonstoneBaseSubmissionAdmin",
    "DragonstoneBaseSubmissionChildAdmin",
    "PVMSplitAdmin",
    "MentorAdmin",
    "EventAdmin",
]


@admin.register(models.DragonstoneBaseSubmission)
class DragonstoneBaseSubmissionAdmin(PolymorphicParentModelAdmin):
    base_model = models.DragonstoneBaseSubmission
    child_models = (
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


@admin.register(models.PVMSplitSubmission)
class PVMSplitAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = models.PVMSplitSubmission
    inlines = [inlines.PVMSplitPointsAdminInline]
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
class MentorAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = models.MentorSubmission
    inlines = [inlines.MentorPointsAdminInline]
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
class EventAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = models.EventSubmission
    inlines = [
        inlines.EventHostPointsAdminInline,
        inlines.EventParticipantPointsAdminInline,
        inlines.EventDonorPointsAdminInline,
    ]
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
