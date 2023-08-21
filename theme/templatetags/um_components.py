from django import template

register = template.Library()


@register.inclusion_tag("theme/components/page_header.html")
def page_header(text, icon=None):
    return {"text": text, "icon": icon}


@register.inclusion_tag("theme/components/simple_input.html")
def simple_input(field, label=None, prefix=""):
    return {"field": field, "label": label, "prefix": prefix}


@register.inclusion_tag("theme/components/textarea_input.html")
def textarea_input(field, label=None, prefix=""):
    return {"field": field, "label": label, "prefix": prefix}


@register.inclusion_tag("theme/components/file_input.html")
def file_input(field, label=None, prefix=""):
    return {"field": field, "label": label, "prefix": prefix}
