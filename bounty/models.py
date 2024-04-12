import json

import requests
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Bounty(models.Model):
    title = models.CharField(max_length=128, default="")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    board = models.ForeignKey("main.Board", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="bounty/image/")
    prize_pool = models.PositiveIntegerField(
        default=0, help_text="Total amount of gp in the prize pool."
    )

    class Meta:
        ordering = ["-start_date"]

    @classmethod
    def get_current_bounty(cls):
        today = timezone.now()
        try:
            current_bounty = cls.objects.get(start_date__lt=today, end_date__gt=today)
        except cls.DoesNotExist:
            return None
        return current_bounty

    def get_submissions(self):
        return self.board.top_unique_submissions().filter(
            date__gte=self.start_date, date__lte=self.end_date, bounty_accepted=True
        )

    def get_most_improved(self):
        raise NotImplementedError

    def on_accepted_submission(self, submission):
        submissions = self.get_submissions()
        try:
            rank = list(submissions).index(submission) + 1
        except ValueError:
            rank = None

        if rank in [1, 2, 3]:
            rank_display = {1: "1st", 2: "2nd", 3: "3rd"}[rank]
            title = "Bounty Claimed"
            users = ", ".join(submission.accounts.values_list("name", flat=True))
            description = f"{users} submitted a time of {submission.value_display()} to claim {rank_display} place."
            data = json.dumps({"embeds": [self.create_embed(title, description)]})
            requests.post(
                settings.BOUNTY_DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )

        if rank == submissions.count():
            title = "Bounty Claimed"
            users = ", ".join(submission.accounts.values_list("name", flat=True))
            description = f"{users} submitted a time of {submission.value_display()} to claim the slowest time of the bounty."
            data = json.dumps({"embeds": [self.create_embed(title, description)]})
            requests.post(
                settings.BOUNTY_DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )

    def create_embed(self, title, description):
        """
        Create json discord embed.
        """
        embed = {
            "color": 0x78350F,
            "title": title,
            "description": description,
            "url": f"https://{settings.DOMAIN}{reverse('bounty:current-bounty')}",
        }
        return embed
