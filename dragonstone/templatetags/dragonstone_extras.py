from django import template

register = template.Library()


@register.simple_tag
def get_event_submission_roles(event_submission, account):
    return event_submission.roles_display(account)
