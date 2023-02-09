import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import reverse

from main import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        record_submissions = models.RecordSubmission.objects.filter(accepted__isnull=True)
        pet_submissions = models.PetSubmission.objects.filter(accepted__isnull=True)
        col_logs_submissions = models.ColLogSubmission.objects.filter(accepted__isnull=True)
        ca_submissions = models.CASubmission.objects.filter(accepted__isnull=True)

        unreviewed_submissions = False
        html_message = f"There are unreviewed submissions for the UM PB leaderboards for the following submission categories:"
        for submissions in [record_submissions, pet_submissions, col_logs_submissions, ca_submissions]:
            if submissions.exists():
                admin_url = reverse(f'admin:main_{submissions.model._meta.model_name}_changelist')
                html_message += f"https://{settings.DOMAIN}{admin_url}?accepted__isnull=True"
                unreviewed_submissions = True

        if unreviewed_submissions and (datetime.datetime.today().timetuple().tm_yday % 2) != 0:
            # send notifications for unreviewed submissions only every other day! (odd-numbered days of the year)
            user_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
            send_mail(
                'UM LeaderBoards - Unreviewed Submissions',
                'There are unreviewed submissions for the UM PB leaderboards. Please Go to https://www.um-osrs.com/admin to review the submissions.',
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                html_message=html_message
            )
