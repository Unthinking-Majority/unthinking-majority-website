from constance import config
from django.contrib import admin
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from account import models


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "rank", "dragonstone_pts", "is_active"]
    list_editable = ["rank"]
    list_filter = ["is_active", "rank"]
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "preferred_name"),
                    "rank",
                    ("is_active", "is_alt"),
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).dragonstone_points()

    @admin.display(description="Dragonstone Points", ordering="dragonstone_pts")
    def dragonstone_pts(self, obj):
        if obj.dragonstone_pts >= int(config.DRAGONSTONE_POINTS_THRESHOLD):
            dragonstone_icon_url = static("dragonstone/img/dragonstone.webp")
            return mark_safe(
                f'{obj.dragonstone_pts} <img src="{dragonstone_icon_url}" style="height: 17px; width: 17px"/>'
            )
        return obj.dragonstone_pts


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
