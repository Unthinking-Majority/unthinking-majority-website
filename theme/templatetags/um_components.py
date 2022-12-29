from django import template

register = template.Library()


@register.inclusion_tag('theme/components/page_header.html')
def page_header(text):
    return {'text': text}
