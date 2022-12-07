from collections import Counter

from django import template
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


@register.inclusion_tag('dashboard/pets_leaderboard.html')
def pets_leaderboard():
    return {'accounts': Account.objects.annotate(num_pets=Count('pets')).order_by('-num_pets').prefetch_related('pets')[:5]}


@register.inclusion_tag('dashboard/recent_achievements.html')
def recent_submission_leaderboard():
    return {'recent_submissions': Submission.objects.accepted().order_by('date')[:5]}


@register.inclusion_tag('dashboard/top_players_leaderboard.html')
def top_players_leaderboard():
    temp = Submission.objects.accepted().values('board').annotate(Max('value')).values_list('account', flat=True)
    first_places = [
        {'account': Account.objects.get(pk=pk), 'val': val}
        for pk, val in Counter(temp).most_common(5)
    ]
    return {'first_places': first_places}


@register.filter
def board_url(board):
    return f'/board/{board.category.slug}/{board.slug}'


@register.filter
def value_display(value, metric):
    if metric == Board.TIME:
        minutes = int(value // 60)
        seconds = value % 60
        return f"{minutes}:{seconds}"
    else:
        return value
