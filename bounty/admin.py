from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from bounty import models
from bounty import forms


@admin.register(models.Bounty)
class BountyAdmin(admin.ModelAdmin):
    form = forms.BountyAdminForm
    autocomplete_fields = ["board"]
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
                    ("board", "prize_pool"),
                    ("start_date", "end_date"),
                    "image",
                ),
            },
        ),
    )

    @admin.display(description="Bounty Name")
    def bounty_name(self, obj):
        return obj.board.name
