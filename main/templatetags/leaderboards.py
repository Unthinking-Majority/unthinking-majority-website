from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count, OuterRef

from account.models import Account
from main import models

register = template.Library()


@register.inclusion_tag('main/dashboard/pets_leaderboard.html')
def pets_leaderboard():
    pet_submissions = models.Submission.objects.accepted().pets()
    account_pks = pet_submissions.values('accounts').annotate(num_pets=Count('accounts')).order_by('-num_pets')
    return {
        'accounts': [Account.objects.get(pk=obj['accounts']) for obj in account_pks]
    }


@register.inclusion_tag('main/dashboard/col_logs_leaderboard.html')
def col_logs_leaderboard():

    # get accepted collection log submissions ; use empty order_by() to clear any ordering
    col_logs_submissions = models.Submission.objects.col_logs().accepted().order_by()

    # create sub query, which grabs the Max col_log value for each account
    sub_query = col_logs_submissions.order_by('accounts', '-value').distinct('accounts').filter(id=OuterRef('id'))

    # annotate each account object with its max col_log value using the previous sub_query
    accounts = Account.objects.annotate(col_logs=sub_query.values('value')[:1])

    # filter out null col_log values, order by descending, return top 15
    accounts = accounts.filter(col_logs__isnull=False).order_by('-col_logs')[:15]

    return {
        'accounts': accounts,
        'max_col_log': settings.MAX_COL_LOG,
    }


@register.inclusion_tag('main/dashboard/recent_achievements.html')
def recent_submission_leaderboard():
    return {
        'recent_submissions': models.Submission.objects.accepted()[:5]
    }


@register.inclusion_tag('main/dashboard/top_players_leaderboard.html')
def top_players_leaderboard():
    accounts = []
    for board in models.Board.objects.all():
        try:
            first_place_accounts = board.submissions.order_by('value').first().accounts.all()
        except AttributeError:
            continue
        accounts += list(first_place_accounts)
    return {'accounts': Counter(accounts).most_common(5)}
