from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from dragonstone import models


@admin.register(models.DragonstonePoints)
class DragonstonePointsAdmin(PolymorphicParentModelAdmin):
    model = models.DragonstonePoints
    child_models = (
        models.FreeformPoints,
        models.RecruitmentPoints,
        models.SotMPoints,
        models.PVMSplitPoints,
        models.MentorPoints,
        models.EventHostPoints,
        models.EventParticipantPoints,
        models.EventDonorPoints,
        models.NewMemberRaidPoints,
    )
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        PolymorphicChildModelFilter,
    ]
    readonly_fields = ["date", "points"]


class DragonstonePointsChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.DragonstonePoints


@admin.register(models.FreeformPoints)
class FreeformPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.FreeformPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "created_by"]
    list_display = ["account", "points", "date", "created_by"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "created_by"),
                    ("points", "date"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.RecruitmentPoints)
class RecruitmentPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.RecruitmentPoints
    show_in_index = True
    autocomplete_fields = ["account", "recruited"]
    readonly_fields = ["date", "points"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "recruited"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.SotMPoints)
class SotMPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.SotMPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    list_display = ["account", "skill", "rank"]
    list_filter = ["skill"]
    readonly_fields = ["date", "points"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "skill", "rank"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.PVMSplitPoints)
class PVMSplitPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.PVMSplitPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.MentorPoints)
class MentorPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.MentorPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.EventHostPoints)
class EventHostPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.EventHostPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.EventParticipantPoints)
class EventParticipantPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.EventParticipantPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.EventDonorPoints)
class EventDonorPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.EventDonorPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )


@admin.register(models.NewMemberRaidPoints)
class NewMemberRaidPointsAdmin(PolymorphicChildModelAdmin):
    base_model = models.NewMemberRaidPoints
    show_in_index = True
    autocomplete_fields = ["account"]
    readonly_fields = ["date", "points"]
    raw_id_fields = ["submission"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("account", "submission"),
                    ("points", "date"),
                ),
            },
        ),
    )
