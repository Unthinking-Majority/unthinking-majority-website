from django import template
from django.conf import settings

from main.models import ContentCategory

register = template.Library()


@register.inclusion_tag('main/navbar.html', takes_context=True)
def navbar(context):
    return {
        'request': context['request'],
        'board': context.get('board', None),
        'content_categories': ContentCategory.objects.all(),
    }


@register.filter
def addstr(str1, str2):
    return str(str1) + str(str2)


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
