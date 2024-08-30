import json

import requests
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone

from main.functions import gp_display


class Bounty(models.Model):
    title = models.CharField(max_length=128, default="")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    board = models.ForeignKey("main.Board", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="bounty/image/")
    event_phrase = models.CharField(max_length=32)
    prize_pool = models.PositiveIntegerField(
        default=0, help_text="Total amount of gp in the prize pool."
    )
    bounty_reason = models.TextField(
        max_length=256,
        help_text="Give a fun reason for why this npc has a bounty placed on their head!",
    )
    enemy_description = models.CharField(
        max_length=128,
        help_text="Give a fun descriptor for what this npc is! A 'nefarious criminal'? Maybe a 'nasty bug'?",
    )

    # Fields for saving the winners after the event is over!
    first_place = models.ForeignKey(
        "account.Account",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="first_place_bounties",
    )
    second_place = models.ForeignKey(
        "account.Account",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="second_place_bounties",
    )
    third_place = models.ForeignKey(
        "account.Account",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="third_place_bounties",
    )

    class Meta:
        ordering = ["-start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_prize_pool = self.prize_pool

    def save(self, *args, **kwargs):
        super(Bounty, self).save(*args, **kwargs)
        if self.prize_pool > self.__original_prize_pool:
            embed = self.create_embed(
                "Bounty Increased",
                f"The prize pool for the bounty has increased to {gp_display(self.prize_pool)}.",
                thumbnail=static("bounty/img/CoinStack.webp"),
            )
            data = json.dumps({"embeds": [embed]})
            requests.post(
                settings.BOUNTY_DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )

    @classmethod
    def get_current_bounty(cls):
        today = timezone.now()
        try:
            current_bounty = cls.objects.get(start_date__lt=today, end_date__gt=today)
        except cls.DoesNotExist:
            return None
        return current_bounty

    def get_submissions(self):
        return self.board.top_unique_submissions(
            start_date=self.start_date,
            end_date=self.end_date,
            exclude_inactive=False,
            bounty_accepted=True,
        )

    def get_slowest_submission(self):
        return (
            self.board.submissions.filter(
                date__gte=self.start_date, date__lte=self.end_date
            )
            .order_by(f"{self.board.content.ordering}value", "date")
            .last()
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

        # Updates for slowest bounty submission if applicable to this bounty
        # all_bounty_submissions = self.board.submissions.filter(
        #     date__gte=self.start_date, date__lte=self.end_date
        # ).order_by(f"{self.board.content.ordering}value", "date")
        # try:
        #     non_unique_rank = list(all_bounty_submissions).index(submission) + 1
        # except ValueError:
        #     non_unique_rank = None
        # if non_unique_rank == all_bounty_submissions.count():
        #     title = "Bounty Claimed"
        #     users = ", ".join(submission.accounts.values_list("name", flat=True))
        #     description = f"{users} submitted a time of {submission.value_display()} to claim the slowest time of the bounty."
        #     data = json.dumps({"embeds": [self.create_embed(title, description)]})
        #     requests.post(
        #         settings.BOUNTY_DISCORD_WEBHOOK_URL,
        #         data=data,
        #         headers={"Content-Type": "application/json"},
        #     )

    def create_embed(self, title, description, thumbnail=None):
        """
        Create json discord embed.
        """
        embed = {
            "color": 0x78350F,
            "title": title,
            "description": description,
            "url": f"https://{settings.DOMAIN}{reverse('bounty:current-bounty')}",
        }

        if not settings.DEBUG and thumbnail:
            embed["thumbnail"] = {"url": thumbnail}

        return embed


class ExtraBountyReward(models.Model):
    bounty = models.ForeignKey(
        "bounty.Bounty", on_delete=models.CASCADE, related_name="extra_rewards"
    )
    title = models.CharField(max_length=32)
    rules = models.CharField(max_length=256, blank=True)
    percent_of_prize_pool = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    winner = models.ForeignKey(
        "account.Account",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="extra_bounty_rewards",
    )
