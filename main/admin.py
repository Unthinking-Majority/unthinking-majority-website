from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

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
    autocomplete_fields = ["content"]
    list_display = ["name", "content", "team_size", "flex_order"]
    list_editable = ["flex_order"]
    list_filter = [
        AutocompleteFilterFactory("Content Category", "content__category"),
        AutocompleteFilterFactory("Content", "content"),
    ]
    search_fields = ["name"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "content", "team_size", "flex_order"),
            },
        ),
    )


@admin.register(models.Pet)
class PetAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(models.Settings)
class SettingsAdmin(admin.ModelAdmin):
    readonly_fields = ["name"]
    list_display = ["display_name", "value"]
    list_editable = ["value"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("display_name", "value"),
                    "name",
                ),
            },
        ),
    )


@admin.register(models.UMNotification)
class UMNotificationAdmin(admin.ModelAdmin):
    search_fields = ["verb"]
