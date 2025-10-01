from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Sum, IntegerField, Value, QuerySet, Q

from dragonstone.models import DragonstonePoints, PVMSplitPoints, GroupCAPoints
from main.config import config
from main.models import Board


class AccountQueryset(QuerySet):
    def dragonstone_points(self, ignore=None, delta=timedelta(0)):
        """
        Return all active accounts queryset with each accounts total dragonstone points annotated
        :ignore: a list of DragonstoneBaseSubmission primary keys to ignore when annotating dragonstone points
        """
        if not ignore:
            ignore = []
        dstone_pts_sum_by_type = (
            DragonstonePoints.objects.accepted()
            .expired(expired=False, delta=delta)
            .filter(~Q(pk__in=ignore))
            .values("account", "polymorphic_ctype")
            .order_by()
            .annotate(pts=Sum("points"))
            .values("account", "pts", "polymorphic_ctype")
        )

        dstone_pts = {}
        capped_pts_ctypes = [
            ContentType.objects.get_for_model(PVMSplitPoints).id,
            ContentType.objects.get_for_model(GroupCAPoints).id,
        ]
        for obj in dstone_pts_sum_by_type:
            if obj["account"] not in dstone_pts.keys():
                dstone_pts[obj["account"]] = {
                    "uncapped": 0,
                    "capped": 0,
                }
            if obj["polymorphic_ctype"] in capped_pts_ctypes:
                dstone_pts[obj["account"]]["capped"] += obj["pts"]
                if dstone_pts[obj["account"]]["capped"] > config.CAPPED_POINTS_MAX:
                    dstone_pts[obj["account"]]["capped"] = config.CAPPED_POINTS_MAX
            else:
                dstone_pts[obj["account"]]["uncapped"] += obj["pts"]

        whens = [
            When(id=account, then=sum([val for val in pts.values()]))
            for account, pts in dstone_pts.items()
        ]
        return self.annotate(
            annotated_dragonstone_pts=Case(
                *whens, output_field=IntegerField(), default=Value(0)
            )
        ).order_by("-annotated_dragonstone_pts", "name")

    def annotate_points(self):
        """
        Return all a queryset of all active accounts with each accounts total record points annotated
        """
        points = [
            config.FIRST_PLACE_PTS,
            config.SECOND_PLACE_PTS,
            config.THIRD_PLACE_PTS,
            config.FOURTH_PLACE_PTS,
            config.FIFTH_PLACE_PTS,
        ]

        account_ids = self.filter(is_active=True).values_list("pk", flat=True)
        accounts = dict(
            zip(account_ids, [0] * len(account_ids))
        )  # initialize of dict where key=account_id and value=0 so we can begin summing their points

        for board in Board.objects.filter(
            is_active=True, content__has_pbs=True
        ).prefetch_related("submissions", "submissions__accounts"):
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
