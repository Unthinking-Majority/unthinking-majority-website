from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Sum, IntegerField, Value, F, QuerySet, Q
from django.db.models.functions import Least

from dragonstone.models import DragonstonePoints, PVMSplitPoints
from main.config import config
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
        points = [
            config.FIRST_PLACE_PTS,
            config.SECOND_PLACE_PTS,
            config.THIRD_PLACE_PTS,
            config.FOURTH_PLACE_PTS,
            config.FIFTH_PLACE_PTS,
        ]
        for board in Board.objects.filter(is_active=True, content__has_pbs=True):
            submissions = board.top_unique_submissions()[:5]

            query = Q(is_active=True)
            for index, submission in enumerate(submissions):
                submission_accounts = submission.accounts.filter(query)

                for account in submission_accounts:
                    accounts[account.pk] += points[index] * board.points_multiplier
                query &= ~Q(pk__in=submission_accounts.values_list("pk"))

        whens = [When(pk=pk, then=pts) for pk, pts in list(accounts.items())]
        return self.annotate(
            points=Case(*whens, default=0, output_field=IntegerField())
        ).order_by("-points")
