from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count, OuterRef

from account.models import Account
from main import models, GRANDMASTER

register = template.Library()


@register.inclusion_tag('main/landing_leaderboards/pets_leaderboard.html')
def pets_leaderboard():
    # get accepted pet submissions
    pet_submissions = models.Submission.objects.accepted().pets()

    # create sub query, to annotate the number of pets per account
    sub_query = pet_submissions.values('accounts').annotate(num_pets=Count('accounts')).filter(accounts__id=OuterRef('id'))

    # annotate num_pets per account using sub query ; filter out null values ; order by number of pets descending
    accounts = Account.objects.annotate(num_pets=sub_query.values('num_pets')[:1]).filter(
        num_pets__isnull=False,
        active=True
    ).order_by('-num_pets')

    return {
        'accounts': accounts[:5]
    }


@register.inclusion_tag('main/landing_leaderboards/col_logs_leaderboard.html')
def col_logs_leaderboard():
    # get accepted collection log submissions ; use empty order_by() to clear any ordering
    col_logs_submissions = models.Submission.objects.col_logs().accepted().order_by().filter(accounts__active=True)

    # create sub query, which grabs the Max col_log value for each account
    sub_query = col_logs_submissions.order_by('accounts', '-value').distinct('accounts').filter(accounts__id=OuterRef('id'))

    # annotate each account object with its max col_log value using the previous sub_query
    accounts = Account.objects.annotate(col_logs=sub_query.values('value')[:1])

    # filter out null col_log values, order by descending, return top 15
    accounts = accounts.filter(col_logs__isnull=False).order_by('-col_logs')[:15]

    return {
        'accounts': accounts,
        'max_col_log': settings.MAX_COL_LOG,
    }


@register.inclusion_tag('main/landing_leaderboards/grandmasters_leaderboard.html')
def grandmasters_leaderboard():
    submissions = models.Submission.objects.combat_achievements().accepted().filter(
        ca_tier=GRANDMASTER,
        accounts__active=True
    ).order_by('date')
    return {
        'submissions': submissions
    }


@register.inclusion_tag('main/landing_leaderboards/recent_achievements.html')
def recent_submission_leaderboard():
    return {
        'recent_submissions': models.Submission.objects.accepted()[:5]
    }


@register.inclusion_tag('main/landing_leaderboards/top_players_leaderboard.html')
def top_players_leaderboard():
    accounts = []
    for board in models.Board.objects.all():
        order = f'{board.content.ordering}value'
        try:
            first_place_accounts = board.submissions.order_by(order).first().accounts.filter(active=True)
        except AttributeError:
            continue
        accounts += list(first_place_accounts)
    return {'accounts': Counter(accounts).most_common(15)}
