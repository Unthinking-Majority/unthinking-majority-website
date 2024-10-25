from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from dragonstone import models


@admin.register(models.DragonstonePoints)
class DragonstonePointsAdmin(admin.ModelAdmin):
    model = models.DragonstonePoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
    ]
    readonly_fields = ["points"]


@admin.register(models.FreeformPoints)
class FreeformPointsAdmin(admin.ModelAdmin):
    model = models.FreeformPoints
    autocomplete_fields = ["account"]
    readonly_fields = ["created_by"]
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
class RecruitmentPointsAdmin(admin.ModelAdmin):
    model = models.RecruitmentPoints
    autocomplete_fields = ["account", "recruited"]
    list_display = ["account", "recruited", "points", "date"]
    readonly_fields = ["points"]

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
class SotMPointsAdmin(admin.ModelAdmin):
    model = models.SotMPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "skill", "rank"]
    list_filter = ["skill"]
    readonly_fields = ["points"]

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
class PVMSplitPointsAdmin(admin.ModelAdmin):
    model = models.PVMSplitPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
class MentorPointsAdmin(admin.ModelAdmin):
    model = models.MentorPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
class EventHostPointsAdmin(admin.ModelAdmin):
    model = models.EventHostPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
class EventParticipantPointsAdmin(admin.ModelAdmin):
    model = models.EventParticipantPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
class EventDonorPointsAdmin(admin.ModelAdmin):
    model = models.EventDonorPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
class NewMemberRaidPointsAdmin(admin.ModelAdmin):
    model = models.NewMemberRaidPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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


@admin.register(models.GroupCAPoints)
class GroupCAPointsAdmin(admin.ModelAdmin):
    model = models.GroupCAPoints
    autocomplete_fields = ["account"]
    list_display = ["account", "points", "date"]
    readonly_fields = ["points"]
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
