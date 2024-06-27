from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from bounty import forms
from bounty import models
from bounty.admin.inlines import ExtraBountyRewardInline


@admin.register(models.Bounty)
class BountyAdmin(admin.ModelAdmin):
    form = forms.BountyAdminForm
    inlines = [ExtraBountyRewardInline]
    autocomplete_fields = ["board", "first_place", "second_place", "third_place"]
    list_display = ["bounty_name", "start_date", "end_date"]
    list_filter = [
        AutocompleteFilterFactory("Board", "board"),
        "start_date",
        "end_date",
    ]
    readonly_fields = ["bounty_name"]
    search_fields = ["board__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "board",
                    "prize_pool",
                    "event_phrase",
                    "bounty_reason",
                    ("start_date", "end_date"),
                    "image",
                    "first_place",
                    "second_place",
                    "third_place",
                ),
            },
        ),
    )

    @admin.display(description="Bounty Name")
    def bounty_name(self, obj):
        return obj.board
