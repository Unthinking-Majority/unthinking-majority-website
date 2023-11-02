from constance import config
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Sum, IntegerField, Value, F
from django.db.models.functions import Least
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from account import models
from dragonstone.models import DragonstonePoints, PVMSplitPoints


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
        queryset = super(AccountAdmin, self).get_queryset(request)

        dstone_pts_sum_by_type = (
            DragonstonePoints.objects.active()
            .values("account", "polymorphic_ctype")
            .order_by()
            .annotate(_pts=Sum("points"))
            .annotate(
                pts=Case(
                    When(
                        polymorphic_ctype=ContentType.objects.get_for_model(
                            PVMSplitPoints
                        ),
                        then=Least(F("_pts"), config.PVM_SPLIT_POINTS_MAX),
                    ),
                    default=F("_pts"),
                ),
            )
            .values("account", "pts")
        )

        dstone_pts = {}
        for obj in dstone_pts_sum_by_type:
            if obj["account"] not in dstone_pts.keys():
                dstone_pts[obj["account"]] = obj["pts"]
            else:
                dstone_pts[obj["account"]] += obj["pts"]

        whens = [When(id=account, then=pts) for account, pts in dstone_pts.items()]
        return queryset.annotate(
            dragonstone_pts=Case(*whens, output_field=IntegerField(), default=Value(0))
        ).order_by("-dragonstone_pts", "name")

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
