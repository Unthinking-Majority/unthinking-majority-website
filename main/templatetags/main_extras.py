from django import template
from django.urls import reverse

from main.models import BoardCategory

register = template.Library()


@register.inclusion_tag('main/navbar.html', takes_context=True)
def navbar(context):
    return {
        'request': context['request'],
        'board': context.get('board', None),
        'board_categories': BoardCategory.objects.all(),
    }


@register.filter
def leaderboard_url(board):
    return reverse('leaderboard', kwargs={'board_category': board.category.slug, 'parent_board_name': board.slug})


@register.filter
def addstr(str1, str2):
    return str(str1) + str(str2)
