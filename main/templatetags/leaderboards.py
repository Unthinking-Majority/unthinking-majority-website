from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count

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
    return {
        'accounts': Account.objects.order_by('-col_logs')[:15],
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
