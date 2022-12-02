from django import template

from main.models import BoardCategory, Board

register = template.Library()


@register.inclusion_tag('navbar.html')
def navbar():
    return {'board_categories': BoardCategory.objects.all()}


@register.filter
def value_display(value, metric):
    if metric == Board.TIME:
        minutes = int(value // 60)
        seconds = value % 60
        return f"{minutes}:{seconds}"
    else:
        return value
