import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.urls import reverse
from polymorphic.models import PolymorphicModel

from achievements import managers, CA_CHOICES
from bounty.models import Bounty
from main import INTEGER, TIME
from main.models import UMNotification
from um.functions import get_file_path


class BaseSubmission(PolymorphicModel):
    UPLOAD_TO = "submission/proof/"

    proof = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    denial_notes = models.TextField(
        blank=True, help_text="Only need to fill out if submission is denied."
    )
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.SubmissionQueryset().as_manager()

    __original_accepted = None

    class Meta:
        ordering = [F("date").desc(nulls_last=True)]
        verbose_name = "Base Submission"
        verbose_name_plural = "All Submissions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_accepted = self.accepted

    def save(self, *args, **kwargs):
        super(BaseSubmission, self).save(*args, **kwargs)
        if self.accepted and self.accepted != self.__original_accepted:
            # get_child_instance seems to return self if there is no child. This works out
            # because this code still runs successfully when a child instance is saved!
            self.get_real_instance().on_accepted()

    def on_creation(self):
        """
        Post to discord um pb webhook the newly accepted submission!
        """
        data = json.dumps(
            {
                "embeds": [self.create_new_submission_embed()],
                "components": self.create_new_submission_components(),
            }
        )
        requests.post(
            settings.UM_SUBMISSIONS_DISCORD_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created submissions.
        """
        fields = [
            {
                "name": "Type",
                "value": self.type_display(),
                "inline": True,
            },
            {
                "name": "Value",
                "value": self.value_display(),
                "inline": True,
            },
            {
                "name": "User(s)",
                "value": self.accounts_display(),
            },
            {
                "name": "Date",
                "value": f"{self.date:%b %d, %Y}",
                "inline": True,
            },
        ]

        if self.notes:
            fields.append(
                {
                    "name": "Notes",
                    "value": self.notes,
                }
            )

        admin_url = reverse(
            f"admin:{self.get_real_instance()._meta.app_label}_{self.get_real_instance()._meta.model_name}_change",
            args=[self.id],
        )

        embed = {
            "color": 0x0099FF,
            "title": "New Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{admin_url}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed

    def create_new_submission_components(self):
        components = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "label": "Accept",
                        "style": 3,
                        "custom_id": "accept-submission",
                    },
                    {
                        "type": 2,
                        "label": "Deny",
                        "style": 4,
                        "custom_id": "deny-submission",
                    },
                ],
            }
        ]
        return components

    def get_rank(self):
        submissions = self.board.top_unique_submissions()
        for rank, submission in enumerate(submissions):
            if submission.id == self.id:
                return rank + 1
        return None

    def send_notifications(self, request):
        self.get_real_instance().send_notifications(request)

    def type_display(self):
        """
        Call the type_display() method from the corresponding child instance of this base submission
        """
        return self.get_real_instance().type_display()

    def value_display(self):
        """
        Call the value_display() method from the corresponding child instance of this base submission
        """
        return self.get_real_instance().value_display()

    def accounts_display(self):
        """
        Call the accounts_display() method from the corresponding child instance of this base submission
        """
        return self.get_real_instance().accounts_display()


class RecordSubmission(BaseSubmission):
    accounts = models.ManyToManyField("account.Account")
    board = models.ForeignKey(
        "main.Board", on_delete=models.CASCADE, related_name="submissions"
    )
    value = models.DecimalField(max_digits=7, decimal_places=2)

    bounty_accepted = models.BooleanField(
        default=False,
        null=True,
        help_text="For record submissions which are made during a Bounty event for the selected Bounty's content. Must be set to true for a submission to be accepted for a given Bounty event.",
    )

    class Meta:
        verbose_name = "Record Submission"
        verbose_name_plural = "Record Submissions"

    def __str__(self):
        return f"{self.board}"

    def send_notifications(self, request):
        if self.accepted is not None:
            verb = f"{'accepted' if self.accepted else 'denied'} your submission for"
            custom_url = reverse("account:profile") if request.user.is_staff else None
            for account in self.accounts.all():
                if account.user:
                    UMNotification.objects.create(
                        actor_object_id=request.user.account.id,
                        actor_content_type=ContentType.objects.get_for_model(
                            request.user.account
                        ),
                        verb=verb,
                        recipient=account.user,
                        action_object_object_id=self.id,
                        action_object_content_type=ContentType.objects.get_for_model(
                            self
                        ),
                        custom_url=custom_url,
                    )

    def type_display(self):
        return self.board.name

    def value_display(self):
        if self.board.content.metric == TIME:
            minutes = int(self.value // 60)
            seconds = self.value % 60
            return f"{minutes}:{float(seconds):05.2f}"
        else:
            return (
                int(self.value) if self.board.content.metric == INTEGER else self.value
            )

    def accounts_display(self):
        return ", ".join([account.display_name for account in self.accounts.all()])

    def on_accepted(self):
        """
        Post to discord um pb webhook the newly accepted submission!
        """
        data = json.dumps({"embeds": [self.create_embed()]})
        requests.post(
            settings.UM_PB_DISCORD_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        bounty = Bounty.get_current_bounty()
        if bounty and self.bounty_accepted:
            bounty.on_accepted_submission(self)

    def get_rank(self):
        submissions = self.board.top_unique_submissions()
        for rank, submission in enumerate(submissions):
            if submission.id == self.id:
                return rank + 1
        return None

    def create_embed(self):
        """
        Create json discord embed.
        """
        fields = [
            {
                "name": "Board",
                "value": str(self.board),
            },
            {
                "name": "User(s)",
                "value": ", ".join(self.accounts.values_list("name", flat=True)),
            },
            {
                "name": self.board.content.metric_name,
                "value": self.value_display(),
                "inline": True,
            },
            {
                "name": "Date",
                "value": f"{self.date:%b %d, %Y}",
                "inline": True,
            },
            {
                "name": "Rank",
                "value": self.get_rank() or "---",
                "inline": True,
            },
        ]
        if self.notes:
            fields.append(
                {
                    "name": "Notes",
                    "value": self.notes,
                }
            )

        embed = {
            "color": 0x0099FF,
            "title": "New Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{self.board.content.leaderboard_url()}?active_board={self.board.slug}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed


class PetSubmission(BaseSubmission):
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    pet = models.ForeignKey("main.Pet", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Pet Submission"
        verbose_name_plural = "Pet Submissions"

    def __str__(self):
        return self.pet.name

    def send_notifications(self, request):
        if self.accepted is not None:
            verb = f"{'accepted' if self.accepted else 'denied'} your submission for"
            custom_url = reverse("account:profile") if request.user.is_staff else None
            if self.account.user:
                UMNotification.objects.create(
                    actor_object_id=request.user.account.id,
                    actor_content_type=ContentType.objects.get_for_model(
                        request.user.account
                    ),
                    verb=verb,
                    recipient=self.account.user,
                    action_object_object_id=self.id,
                    action_object_content_type=ContentType.objects.get_for_model(self),
                    custom_url=custom_url,
                )

    def type_display(self):
        return "Pet"

    def value_display(self):
        return self.pet.name

    def accounts_display(self):
        return self.account.display_name

    def on_accepted(self):
        return


class ColLogSubmission(BaseSubmission):
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    col_logs = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(settings.MAX_COL_LOG)]
    )

    class Meta:
        verbose_name = "Collection Log Submission"
        verbose_name_plural = "Collection Log Submissions"

    def __str__(self):
        return f"{self.col_logs}/{settings.MAX_COL_LOG} Collection Logs"

    def send_notifications(self, request):
        if self.accepted is not None:
            verb = f"{'accepted' if self.accepted else 'denied'} your submission for"
            custom_url = reverse("account:profile") if request.user.is_staff else None
            if self.account.user:
                UMNotification.objects.create(
                    actor_object_id=request.user.account.id,
                    actor_content_type=ContentType.objects.get_for_model(
                        request.user.account
                    ),
                    verb=verb,
                    recipient=self.account.user,
                    action_object_object_id=self.id,
                    action_object_content_type=ContentType.objects.get_for_model(self),
                    custom_url=custom_url,
                )

    def type_display(self):
        return "Collection Logs"

    def value_display(self):
        return f"{self.col_logs}/{settings.MAX_COL_LOG}"

    def accounts_display(self):
        return self.account.display_name

    def on_accepted(self):
        return


class CASubmission(BaseSubmission):
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    ca_tier = models.IntegerField(
        choices=CA_CHOICES,
        verbose_name="Combat Achievement Tier",
    )

    class Meta:
        verbose_name = "Combat Achievement Submission"
        verbose_name_plural = "Combat Achievement Submissions"

    def __str__(self):
        return f"{self.get_ca_tier_display()} tier"

    def send_notifications(self, request):
        if self.accepted is not None:
            verb = f"{'accepted' if self.accepted else 'denied'} your submission for"
            custom_url = reverse("account:profile") if request.user.is_staff else None
            if self.account.user:
                UMNotification.objects.create(
                    actor_object_id=request.user.account.id,
                    actor_content_type=ContentType.objects.get_for_model(
                        request.user.account
                    ),
                    verb=verb,
                    recipient=self.account.user,
                    action_object_object_id=self.id,
                    action_object_content_type=ContentType.objects.get_for_model(self),
                    custom_url=custom_url,
                )

    def type_display(self):
        return "Combat Achievement"

    def value_display(self):
        return self.get_ca_tier_display()

    def accounts_display(self):
        return self.account.display_name

    def on_accepted(self):
        return


class Hiscores(models.Model):
    account = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="hiscores"
    )
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    rank_overall = models.IntegerField(default=0)

    class Meta:
        ordering = ["-score", "rank_overall"]
        unique_together = [("account", "content")]
        verbose_name = "Hiscores"
        verbose_name_plural = "Hiscores"

    def __str__(self):
        return (
            f"{self.account.display_name} - {self.content.hiscores_name} {self.score}kc"
        )
