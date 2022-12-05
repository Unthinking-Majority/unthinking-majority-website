from django import template
from django.db.models import Count

from account.models import Account
from main.models import BoardCategory, Board

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
