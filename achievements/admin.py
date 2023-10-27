from admin_auto_filters.filters import AutocompleteFilterFactory
from django.conf import settings
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from achievements import models


@admin.register(models.BaseSubmission)
class BaseSubmissionAdmin(PolymorphicParentModelAdmin):
    base_model = models.BaseSubmission
    child_models = (
        models.RecordSubmission,
        models.PetSubmission,
        models.ColLogSubmission,
        models.CASubmission,
    )
    list_display = [
        "_type_display",
        "_accounts_display",
        "_value_display",
        "proof",
        "date",
        "accepted",
        "_accepted_display",
    ]
    list_editable = ["accepted"]
    list_filter = ["accepted", "date", PolymorphicChildModelFilter]

    @admin.display(description="Type")
    def _type_display(self, obj):
        return obj.type_display()

    @admin.display(description="Account(s)")
    def _accounts_display(self, obj):
        return obj.accounts_display()

    @admin.display(description="Value")
    def _value_display(self, obj):
        return obj.value_display()

    @admin.display(description="", ordering="accepted", boolean=True)
    def _accepted_display(self, obj):
        return obj.accepted


class BaseSubmissionChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.BaseSubmission


@admin.register(models.RecordSubmission)
class RecordSubmissionAdmin(PolymorphicChildModelAdmin):
    base_model = models.RecordSubmission
    autocomplete_fields = ["accounts", "board"]
    list_display = [
        "accounts_display",
        "board",
        "time_display",
        "proof",
        "date",
        "accepted",
    ]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Accounts", "accounts"),
        AutocompleteFilterFactory("Content", "board__content"),
        AutocompleteFilterFactory("Board", "board"),
        "accepted",
        "date",
    ]
    readonly_fields = ["time_display"]
    search_fields = ["accounts__name", "board__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "accounts",
                    "board",
                    ("value", "time_display"),
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)

    @admin.display(description="Accounts")
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list("name", flat=True))

    @admin.display(description="Time Display")
    def time_display(self, obj):
        return obj.value_display()


@admin.register(models.PetSubmission)
class PetSubmissionAdmin(PolymorphicChildModelAdmin):
    base_model = models.PetSubmission
    autocomplete_fields = ["account", "pet"]
    list_display = ["account", "pet", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        AutocompleteFilterFactory("Pet", "pet"),
        "accepted",
        "date",
    ]
    search_fields = ["account__name", "pet__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "pet",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)


@admin.register(models.ColLogSubmission)
class ColLogSubmissionAdmin(PolymorphicChildModelAdmin):
    base_model = models.ColLogSubmission
    autocomplete_fields = ["account"]
    list_display = ["account", "col_logs_display", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        "accepted",
        "date",
    ]
    search_fields = ["account__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "col_logs",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)

    @admin.display(description="Collections Logged", ordering="col_logs")
    def col_logs_display(self, obj):
        return f"{obj.col_logs}/{settings.MAX_COL_LOG}"


@admin.register(models.CASubmission)
class CASubmissionAdmin(PolymorphicChildModelAdmin):
    base_model = models.CASubmission
    autocomplete_fields = ["account"]
    list_display = ["account", "ca_tier", "proof", "date", "accepted"]
    list_editable = ["accepted"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        "ca_tier",
        "accepted",
        "date",
    ]
    search_fields = ["account__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "account",
                    "ca_tier",
                    ("notes", "denial_notes"),
                    ("proof", "date", "accepted"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)
