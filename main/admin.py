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
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = [
        "name",
        "category",
        "metric",
        "metric_name",
        "is_pb",
        "can_be_split",
        "can_be_mentored",
    ]
    list_editable = ["is_pb", "can_be_split", "can_be_mentored"]
    list_filter = [
        AutocompleteFilterFactory("Content Category", "category"),
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
                    ("is_pb", "can_be_split", "can_be_mentored"),
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
    list_display = ["name", "content", "team_size"]
    list_filter = [
        AutocompleteFilterFactory("Content Category", "content__category"),
        AutocompleteFilterFactory("Content", "content"),
    ]
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "content", "team_size"),
            },
        ),
        (
            "Other Options",
            {
                "fields": ("slug",),
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
