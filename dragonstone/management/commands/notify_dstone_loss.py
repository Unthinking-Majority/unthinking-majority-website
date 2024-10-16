from datetime import timedelta

from django.core.management.base import BaseCommand

from account.models import Account
from main.config import config


class Command(BaseCommand):
    help = "Notify any loss of dragonstone rank for all users. Run once every hour automatically through a scheduler."

    def handle(self, *args, **options):
        # accounts who have dstone as of now
        current_dstones = Account.objects.dragonstone_points().filter(
            annotated_dragonstone_pts__gte=config.DRAGONSTONE_POINTS_THRESHOLD
        )

        # accounts who had dstone as of an hour ago
        prev_dstones = Account.objects.dragonstone_points(
            delta=timedelta(hours=-1)
        ).filter(annotated_dragonstone_pts__gte=config.DRAGONSTONE_POINTS_THRESHOLD)

        for account in prev_dstones:
            if account not in current_dstones:
                account.notify_dstone_status_change()
