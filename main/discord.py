import logging

import requests
from django.db import transaction

logger = logging.getLogger(__name__)


def post_webhook(url, payload):
    """
    Post a JSON payload to a Discord webhook once the current transaction commits.
    Failures are logged (which also reports them to Sentry) and never raised, so Discord being down can't block saving.
    """
    if not url:
        return
    transaction.on_commit(lambda: _post(url, payload))


def _post(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Posting to a Discord webhook failed")
