from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException
from wagtail.models import Site

from bounty.models import Bounty
from main.models import ContentCategory, UMNotification

register = template.Library()


@register.inclusion_tag("main/navbar/navbar.html", takes_context=True)
def navbar(context):
    menu_pages = (
        Site.objects.get(is_default_site=True)
        .root_page.get_children()
        .filter(show_in_menus=True)
    )
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
        "menu_pages": menu_pages,
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


@register.simple_tag
def get_page_authors(page):
    """
    For use only with wagtail Page models. Return a list of all authors.
    """
    return ", ".join(
        set([revision.user.account.display_name for revision in page.revisions.all()])
    )


@register.filter
def mult(val, multiplier):
    return val * multiplier


@register.simple_tag(name="embed")
def embed_tag(url, max_width=None, max_height=None):
    """
    Override wagtailembeds_tags embed_tag so we can pass max_height argument.
    """
    try:
        embed = embeds.get_embed(url, max_width=max_width, max_height=max_height)
        return mark_safe(embed.html)
    except EmbedException:
        return ""
