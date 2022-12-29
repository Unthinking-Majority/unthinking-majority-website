from collections import Counter

from django import template
from django.conf import settings
from django.db.models import Count, Max

from account.models import Account
from main.models import BoardCategory, Board, Submission

register = template.Library()


@register.inclusion_tag('navbar.html', takes_context=True)
def navbar(context):
    return {
        'request': context['request'],
        'board': context.get('board', None),
        'board_categories': BoardCategory.objects.all(),
    }


@register.inclusion_tag('main/dashboard/pets_leaderboard.html')
def pets_leaderboard():
    pet_submissions = Submission.objects.accepted().pets()
    account_pks = pet_submissions.values('accounts').annotate(num_pets=Count('accounts')).order_by('-num_pets')
    return {
        'accounts': [Account.objects.get(pk=obj['accounts']) for obj in account_pks]
    }


@register.inclusion_tag('main/dashboard/col_logs_leaderboard.html')
def col_logs_leaderboard():
    return {
        'accounts': Account.objects.order_by('-col_logs')[:5],
        'max_col_log': settings.MAX_COL_LOG,
    }


@register.inclusion_tag('main/dashboard/recent_achievements.html')
def recent_submission_leaderboard():
    return {
        'recent_submissions': Submission.objects.accepted()[:5]
    }


@register.inclusion_tag('main/dashboard/top_players_leaderboard.html')
def top_players_leaderboard():
    temp = Submission.objects.accepted().records().values('board').annotate(Max('value')).values_list('accounts', flat=True)
    first_places = [
        {'account': Account.objects.get(pk=pk), 'val': val}
        for pk, val in Counter(temp).most_common(5)
    ]
    return {'first_places': first_places}


@register.filter
def board_url(board):
    return f'/board/{board.category.slug}/{board.slug}'


@register.filter
def get_metric_display(value):
    for val, display in Board.METRIC_CHOICES:
        if val == value:
            return display
    return ''
