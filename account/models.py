from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.db.models import Max, Min

from account import ACCOUNT_RANK_CHOICES
from achievements import CA_DICT
from achievements.models import CASubmission, ColLogSubmission, PetSubmission
from dragonstone.models import (
    EventSubmission,
    FreeformSubmission,
    MentorSubmission,
    PVMSplitSubmission,
    RecruitmentSubmission,
    SotMSubmission,
)
from um.functions import get_file_path


class Account(models.Model):
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=256, help_text="In game name.", unique=True)
    is_active = models.BooleanField(default=True)
    rank = models.PositiveIntegerField(
        choices=ACCOUNT_RANK_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return self.name

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
        recruitment_pts = RecruitmentSubmission.annotate_dragonstone_pts(account=self)
        sotm_pts = SotMSubmission.annotate_dragonstone_pts(account=self)
        pvm_splits_pts = PVMSplitSubmission.annotate_dragonstone_pts(account=self)
        mentor_pts = MentorSubmission.annotate_dragonstone_pts(account=self)
        event_pts = EventSubmission.annotate_dragonstone_pts(account=self)
        freeform_pts = FreeformSubmission.annotate_dragonstone_pts(account=self)
        return (
            recruitment_pts
            + sotm_pts
            + pvm_splits_pts
            + mentor_pts
            + event_pts
            + freeform_pts
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
