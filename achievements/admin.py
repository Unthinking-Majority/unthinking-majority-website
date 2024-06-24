from admin_auto_filters.filters import AutocompleteFilterFactory
from django.conf import settings
from django.contrib import admin
from django.db.models import Case, When, Value
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from achievements import models
from achievements.forms import (
    RecordSubmissionAdminForm,
    RecordSubmissionChangelistAdminForm,
)
from bounty.models import Bounty


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

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)

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
    form = RecordSubmissionAdminForm
    show_in_index = True
    autocomplete_fields = ["accounts", "board"]
    list_display = [
        "accounts_display",
        "board",
        "time_display",
        "proof",
        "date",
        "accepted",
        "bounty_accepted",
        "has_bounty",
    ]
    list_editable = ["accepted", "bounty_accepted"]
    list_filter = [
        AutocompleteFilterFactory("Accounts", "accounts"),
        AutocompleteFilterFactory("Content", "board__content"),
        AutocompleteFilterFactory("Board", "board"),
        "accepted",
        "date",
    ]
    readonly_fields = ["time_display", "has_bounty"]
    search_fields = ["accounts__name", "board__name"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "accounts",
                    "board",
                    ("value", "time_display"),
                    "accepted",
                    "bounty_accepted",
                    ("notes", "denial_notes"),
                    ("proof", "date"),
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        bounty = Bounty.get_current_bounty()
        if bounty:
            queryset = queryset.annotate(
                has_bounty=Case(When(board=bounty.board, then=True), default=False)
            )
        else:
            queryset = queryset.annotate(has_bounty=Value(False))
        return queryset

    def save_model(self, request, obj, form, change):
        if change and "accepted" in form.changed_data:
            obj.send_notifications(request)
        return super().save_model(request, obj, form, change)

    def get_changelist_formset(self, request, **kwargs):
        kwargs["formset"] = RecordSubmissionChangelistAdminForm
        return super().get_changelist_formset(request, **kwargs)

    @admin.display(description="Accounts")
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list("name", flat=True))

    @admin.display(description="Time Display")
    def time_display(self, obj):
        return obj.value_display()

    @admin.display(description="Has Active Bounty", boolean=True)
    def has_bounty(self, obj):
        return obj.has_bounty


@admin.register(models.PetSubmission)
class PetSubmissionAdmin(PolymorphicChildModelAdmin):
    base_model = models.PetSubmission
    show_in_index = True
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
    show_in_index = True
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
    show_in_index = True
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


@admin.register(models.Hiscores)
class HiscoresAdmin(admin.ModelAdmin):
    autocomplete_fields = ["account", "content"]
    search_fields = ["account__name", "content__name"]
    list_display = ["account", "content", "rank_overall", "score"]
    list_filter = [
        AutocompleteFilterFactory("Account", "account"),
        AutocompleteFilterFactory("Content", "content"),
    ]
