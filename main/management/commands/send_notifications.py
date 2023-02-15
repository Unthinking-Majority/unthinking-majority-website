import datetime

from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import reverse

from achievements import models as achievements_models
from dragonstone import models as dragonstone_models


class Command(BaseCommand):
    def handle(self, *args, **options):

        submissions = achievements_models.BaseSubmission.objects.filter(accepted__isnull=True)
        if submissions.exists() and (datetime.datetime.today().timetuple().tm_yday % 2) != 0:
            # send notifications for unreviewed submissions only every other day! (odd-numbered days of the year)
            achievements_notifications_group = Group.objects.get(name='Achievements Notifications')
            user_emails = User.objects.filter(is_staff=True, groups=achievements_notifications_group).values_list('email', flat=True)
            send_mail(
                'UM LeaderBoards - Unreviewed Submissions',
                'There are unreviewed submissions for the UM PB leaderboards. Please Go to https://www.um-osrs.com/admin to review the submissions.',
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                html_message=f"There are unreviewed submissions for the UM PB leaderboards. "
                             f"Click here to review the submissions: https://{settings.DOMAIN}{reverse('admin:achievements_basesubmission_changelist')}?accepted__isnull=True"
            )

        submissions = dragonstone_models.DragonstoneBaseSubmission.objects.filter(accepted__isnull=True)
        if submissions.exists() and (datetime.datetime.today().timetuple().tm_yday % 2) != 0:
            # send notifications for unreviewed submissions only every other day! (odd-numbered days of the year)
            dragonstone_notifications_group = Group.objects.get(name='Dragonstone Notifications')
            user_emails = User.objects.filter(is_staff=True, groups=dragonstone_notifications_group).values_list('email', flat=True)
            send_mail(
                'UM Dragonstone - Unreviewed Submissions',
                'There are unreviewed dragonstone submissions. Please Go to https://www.um-osrs.com/admin to review the submissions.',
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                html_message=f"There are unreviewed dragonstone submissions. "
                             f"Click here to review the submissions: https://{settings.DOMAIN}{reverse('admin:dragonstone_dragonstonebasesubmission_changelist')}?accepted__isnull=True"
            )
