from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count, OuterRef

from account.models import Account
from achievements import GRANDMASTER
from achievements.models import (
    BaseSubmission,
    PetSubmission,
    ColLogSubmission,
    CASubmission,
)
from main.models import Board

register = template.Library()


@register.inclusion_tag(
    "main/landing_leaderboards/pets_leaderboard.html", takes_context=True
)
def pets_leaderboard(context):
    # get accepted pet submissions
    pet_submissions = PetSubmission.objects.accepted()

    # create sub query, to annotate the number of pets per account
    sub_query = (
        pet_submissions.values("account")
        .annotate(num_pets=Count("account"))
        .filter(account__id=OuterRef("id"))
    )

    # annotate num_pets per account using sub query ; filter out null values ; order by number of pets descending
    accounts = (
        Account.objects.annotate(num_pets=sub_query.values("num_pets")[:1])
        .filter(num_pets__isnull=False, is_active=True)
        .order_by("-num_pets")
    )

    return {"request": context["request"], "accounts": accounts[:5]}


@register.inclusion_tag("main/landing_leaderboards/col_logs_leaderboard.html")
def col_logs_leaderboard():
    # get accepted collection log submissions ; use empty order_by() to clear any ordering
    col_logs_submissions = (
        ColLogSubmission.objects.accepted().order_by().filter(account__is_active=True)
    )

    # create sub query, which grabs the Max col_log value for each account
    sub_query = (
        col_logs_submissions.order_by("account", "-col_logs")
        .distinct("account")
        .filter(account__id=OuterRef("id"))
    )

    # annotate each account object with its max col_log value using the previous sub_query
    accounts = Account.objects.annotate(col_logs=sub_query.values("col_logs")[:1])

    # filter out null col_log values, order by descending, return top 15
    accounts = accounts.filter(col_logs__isnull=False).order_by("-col_logs")[:15]

    return {
        "accounts": accounts,
        "max_col_log": settings.MAX_COL_LOG,
    }


@register.inclusion_tag(
    "main/landing_leaderboards/grandmasters_leaderboard.html", takes_context=True
)
def grandmasters_leaderboard(context):
    submissions = (
        CASubmission.objects.accepted()
        .filter(ca_tier=GRANDMASTER, account__is_active=True)
        .order_by("date")
    )
    return {"request": context["request"], "submissions": submissions}


@register.inclusion_tag(
    "main/landing_leaderboards/recent_submissions_leaderboard.html", takes_context=True
)
def recent_submission_leaderboard(context):
    return {
        "request": context["request"],
        "recent_submissions": [
            obj.get_real_instance()
            for obj in BaseSubmission.objects.filter(accepted=True)[:5]
        ],
    }


@register.inclusion_tag("main/landing_leaderboards/top_players_leaderboard.html")
def top_players_leaderboard():
    accounts = []
    for board in Board.objects.all():
        order = f"{board.content.ordering}value"
        try:
            first_place_accounts = (
                board.submissions.active()
                .order_by(order)
                .first()
                .accounts.filter(is_active=True)
            )
        except AttributeError:
            continue
        accounts += list(first_place_accounts)
    return {"accounts": Counter(accounts).most_common(15)}
