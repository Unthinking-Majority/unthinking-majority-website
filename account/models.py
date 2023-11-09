from datetime import timedelta

from constance import config
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max, Min

from account import ACCOUNT_RANK_CHOICES
from account import managers
from achievements import CA_DICT
from achievements.models import CASubmission, ColLogSubmission, PetSubmission
from um.functions import get_file_path


class Account(models.Model):
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
    is_alt = models.BooleanField(
        default=False,
        help_text="Check if this is an alt account. Doesn't affect anything on the site; used only for helping admins.",
    )
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
        return CA_DICT.get(ca_tier, "None")

    def dragonstone_pts(self):
        """
        Return total amount of dragonstone points for this account.
        """
        return (
            self.__class__.objects.dragonstone_points().get(id=self.id).dragonstone_pts
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
