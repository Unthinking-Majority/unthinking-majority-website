from django import template

from main.models import BoardCategory

register = template.Library()


@register.inclusion_tag('navbar.html')
def navbar():
    return {'board_categories': BoardCategory.objects.all()}
