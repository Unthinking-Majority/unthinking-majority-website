from django.contrib import admin
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from account import models
from main.config import config


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    list_display = [
        "name",
        "preferred_name",
        "discord_id",
        "rank",
        "dragonstone_pts",
        "is_active",
    ]
    list_editable = ["rank", "discord_id"]
    list_filter = ["is_active", "rank"]
    search_fields = ["name", "preferred_name", "discord_id"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "preferred_name",
                    "discord_id",
                    "user",
                    "rank",
                    "is_active",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).dragonstone_points()

    @admin.display(
        description="Dragonstone Points", ordering="annotated_dragonstone_pts"
    )
    def dragonstone_pts(self, obj):
        if obj.annotated_dragonstone_pts >= config.DRAGONSTONE_POINTS_THRESHOLD:
            dragonstone_icon_url = static("dragonstone/img/dragonstone.webp")
            return mark_safe(
                f'{obj.annotated_dragonstone_pts} <img src="{dragonstone_icon_url}" style="height: 17px; width: 17px"/>'
            )
        return obj.annotated_dragonstone_pts


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
