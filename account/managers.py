from constance import config
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Sum, IntegerField, Value, F, QuerySet, Q
from django.db.models.functions import Least

from dragonstone.models import DragonstonePoints, PVMSplitPoints
from main.models import Board


class AccountQueryset(QuerySet):
    def dragonstone_points(self):
        """
        Return all active accounts queryset with each accounts total dragonstone points annotated
        """
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

    def annotate_points(self):
        """
        Return all active accounts queryset with each accounts total points annotated
        """
        accounts_ids = self.filter(is_active=True).values_list("pk", flat=True)
        accounts = dict(zip(accounts_ids, [0] * len(accounts_ids)))
        first_pts = config.FIRST_PLACE_PTS
        second_pts = config.SECOND_PLACE_PTS
        third_pts = config.THIRD_PLACE_PTS

        for board in Board.objects.all():
            submissions = board.sort_submissions()[:3]

            if submissions.exists():
                first_place_accounts = submissions.first().accounts.filter(
                    is_active=True
                )
                for account in first_place_accounts:
                    accounts[account.pk] += first_pts * board.points_multiplier

                if len(submissions) >= 2:
                    second_place_accounts = submissions[1].accounts.filter(
                        Q(is_active=True)
                        & ~Q(id__in=first_place_accounts.values_list("pk"))
                    )
                    for account in second_place_accounts:
                        accounts[account.pk] += second_pts * board.points_multiplier

                    if len(submissions) >= 3:
                        third_place_accounts = submissions[2].accounts.filter(
                            Q(is_active=True)
                            & ~Q(
                                Q(id__in=first_place_accounts.values_list("pk"))
                                | Q(id__in=second_place_accounts.values_list("pk"))
                            )
                        )
                        for account in third_place_accounts:
                            accounts[account.pk] += third_pts * board.points_multiplier
        whens = [When(pk=pk, then=pts) for pk, pts in list(accounts.items())]
        return self.annotate(
            points=Case(*whens, default=0, output_field=IntegerField())
        ).order_by("-points")
