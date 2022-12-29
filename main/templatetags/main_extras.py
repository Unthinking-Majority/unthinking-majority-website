from django import template

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
def board_url(board):
    return f'/board/{board.category.slug}/{board.slug}'
