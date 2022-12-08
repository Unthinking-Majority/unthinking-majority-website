from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import reverse

from main.models import Submission


class Command(BaseCommand):
    def handle(self, *args, **options):
        submissions = Submission.objects.filter(accepted__isnull=True)
        if submissions.exists():
            # send mail
            user_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            send_mail(
                'UM LeaderBoards - Unreviewed Submissions',
                'There are unreviewed submissions for the UM PB leaderboards. Go to https://www.um-osrs.com/admin to resolve review the submissions.',
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                html_message=f"There are unreviewed submissions for the UM PB leaderboards. "
                             f"Go to https://www.um-osrs.com/admin to resolve review the submissions, or click here "
                             f"https://{settings.DOMAIN}{reverse('admin:main_submission_changelist')}?accepted__isnull=True"
            )
