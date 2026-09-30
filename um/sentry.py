import sentry_sdk


def before_send(event, hint):
    """
    Only the user's id and username are sent to Sentry: no IPs, cookies or headers.
    """
    request = event.get("request")
    if request:
        for key in ("headers", "cookies", "env"):
            request.pop(key, None)
    user = event.get("user")
    if user:
        user.pop("ip_address", None)
    return event


class SentryUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            sentry_sdk.set_user(
                {"id": request.user.pk, "username": request.user.get_username()}
            )
        return self.get_response(request)
