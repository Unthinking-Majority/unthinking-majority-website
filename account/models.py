import json
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max, Min
from django.urls import reverse

from account import ACCOUNT_RANK_CHOICES
from account import managers
from achievements import CA_DICT
from achievements.models import CASubmission, ColLogSubmission, PetSubmission
from main.config import config
from main.models import Board
from um.functions import get_file_path


class Account(models.Model):
    discord_id = models.CharField(max_length=32, unique=True)
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=256, help_text="In game name.", unique=True)
    preferred_name = models.CharField(
        max_length=256,
        help_text="Preferred name to display on website.",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    rank = models.PositiveIntegerField(
        choices=ACCOUNT_RANK_CHOICES, null=True, blank=True
    )

    objects = managers.AccountQueryset.as_manager()

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.preferred_name or self.name

    def pets(self):
        return PetSubmission.objects.accepted().filter(account=self.id)

    def col_logs(self):
        return (
            ColLogSubmission.objects.accepted()
            .filter(account=self.id)
            .aggregate(Max("col_logs"))["col_logs__max"]
            or 0
        )

    def ca_tier(self):
        ca_tier = (
            CASubmission.objects.accepted()
            .filter(account=self.id)
            .aggregate(Min("ca_tier"))["ca_tier__min"]
        )
        return CA_DICT.get(ca_tier, None)

    def achievements_pts(self):
        """
        Return total amount of achievements points for this account.
        """
        return self.__class__.objects.annotate_points().get(id=self.id).points

    def dragonstone_pts(self, ignore=None):
        """
        Return total amount of dragonstone points for this account.
        """
        if not ignore:
            ignore = []
        return (
            self.__class__.objects.dragonstone_points(ignore=ignore)
            .get(id=self.id)
            .dragonstone_pts
        )

    def dragonstone_expiration_date(self):
        """
        Return date this account will lose the dragonstone rank with the current set of points they have.
        """
        pts = 0
        expiration_date = None
        for dstone_pts in self.dragonstone_points.active().order_by("-date"):
            pts += dstone_pts.points
            if pts >= config.DRAGONSTONE_POINTS_THRESHOLD:
                expiration_date = dstone_pts.date
                break
        return expiration_date + timedelta(days=config.DRAGONSTONE_EXPIRATION_PERIOD)

    def create_update_dstone_status_embed(self):
        """
        Create json discord embed.
        """
        if self.dragonstone_pts() >= config.DRAGONSTONE_POINTS_THRESHOLD:
            description = f"<@{self.discord_id}> has gained enough points for the rank of dragonstone!"
        else:
            description = f"<@{self.discord_id}> has lost their dragonstone rank."
        embed = {
            "color": 0x0099FF,
            "title": f"Dragonstone Rank Update",
            "description": description,
            "url": f"https://{settings.DOMAIN}{reverse('admin:account_account_changelist')}",
        }

        return embed

    def update_dstone_status(self):
        """
        Post updates to the #dragonstone-updates channel to notify changing of
        dragonstone rank for this account
        """
        data = json.dumps({"embeds": [self.create_update_dstone_status_embed()]})
        requests.post(
            settings.DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )


class UserCreationSubmission(models.Model):
    """
    Used to moderate account creation.
    """

    UPLOAD_TO = "submission/proof/"

    account = models.OneToOneField("account.Account", on_delete=models.CASCADE)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=128)
    accepted = models.BooleanField(null=True)
    proof = models.ImageField(upload_to=get_file_path)
    phrase = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        super(UserCreationSubmission, self).save(*args, **kwargs)
        if self.accepted is not None:
            if self.accepted:
                user_form = UserCreationForm(
                    {
                        "username": self.username,
                        "password1": self.password,
                        "password2": self.password,
                    }
                )
                user = user_form.save(commit=True)

                self.account.user = user
                self.account.save()
            self.delete()

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
        if config.UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL:
            requests.post(
                config.UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created submissions.
        """
        fields = [
            {
                "name": "Account",
                "value": self.account.name,
                "inline": True,
            },
            {
                "name": "Username",
                "value": self.username,
                "inline": True,
            },
            {
                "name": "Phrase",
                "value": self.phrase,
            },
        ]

        admin_url = reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[self.id],
        )

        embed = {
            "color": 0x0099FF,
            "title": "New User Creation Submission",
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
                        "custom_id": f"user-creation-accept-submission-{self.pk}",
                    },
                    {
                        "type": 2,
                        "label": "Deny",
                        "style": 4,
                        "custom_id": f"user-creation-deny-submission-{self.pk}",
                    },
                ],
            }
        ]
        return components
