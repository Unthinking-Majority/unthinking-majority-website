from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from notifications.models import Notification

from main import models


@admin.register(models.ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",), "hiscores_name": ("name",)}
    search_fields = ["name"]
    list_display = [
        "name",
        "category",
        "metric",
        "metric_name",
        "has_pbs",
        "has_hiscores",
        "can_be_mentored",
        "can_be_split",
    ]
    list_filter = [
        AutocompleteFilterFactory("Content Category", "category"),
        "difficulty",
        "has_pbs",
        "has_hiscores",
        "can_be_mentored",
        "can_be_split",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "difficulty",
                    "icon",
                    (
                        "has_pbs",
                        "can_be_split",
                        "can_be_mentored",
                        "has_hiscores",
                        "hiscores_name",
                    ),
                ),
            },
        ),
        (
            "Other Options",
            {
                "fields": (
                    "slug",
                    ("metric", "metric_name"),
                    ("ordering", "order"),
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["content"]
    list_display = [
        "name",
        "content",
        "team_size",
        "points_multiplier",
        "is_active",
    ]
    list_editable = ["points_multiplier"]
    list_filter = [
        AutocompleteFilterFactory("Content Category", "content__category"),
        AutocompleteFilterFactory("Content", "content"),
        "team_size",
        "is_active",
    ]
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "content", "team_size", "points_multiplier"),
            },
        ),
        (
            "Other Options",
            {
                "fields": ("is_active", "slug"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(models.Pet)
class PetAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(models.UMNotification)
class UMNotificationAdmin(admin.ModelAdmin):
    search_fields = ["verb"]


admin.site.unregister(
    Notification
)  # unregister Notification model from admin, since we have our own UMNotification model + admin
