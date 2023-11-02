from django import template
from django.conf import settings

from bounty.models import Bounty
from main.models import ContentCategory
from main.models import UMNotification

register = template.Library()


@register.inclusion_tag("main/navbar.html", takes_context=True)
def navbar(context):
    if context["request"].user.is_authenticated:
        notifications = UMNotification.objects.filter(
            recipient=context["request"].user
        ).unread()
    else:
        notifications = None
    return {
        "request": context["request"],
        "board": context.get("board", None),
        "notifications": notifications,
        "bounty": Bounty.get_current_bounty(),
        "content_categories": ContentCategory.objects.all(),
    }


@register.filter
def addstr(str1, str2):
    return str(str1) + str(str2)


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def gp_display(val):
    """
    Format val into osrs gp display value.
    0 - 99,999 => return value
    100,000 - 9,999,999 => return value in thousands (100k, 9999k)
    10,000,000 and up =>  return value in millions (10m)
    """
    val = int(val)
    if val <= 99999:
        return val
    elif 100000 <= val <= 9999999:
        return f"{val // 1000}k"
    elif 10000000 <= val:
        return f"{val // 1000000}M"
