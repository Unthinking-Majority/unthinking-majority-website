from constance import config
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Sum, IntegerField, Value, F, QuerySet
from django.db.models.functions import Least

from dragonstone.models import DragonstonePoints, PVMSplitPoints


class AccountQueryset(QuerySet):
    def dragonstone_points(self):
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
        return self.annotate(
            dragonstone_pts=Case(*whens, output_field=IntegerField(), default=Value(0))
        ).order_by("-dragonstone_pts", "name")
