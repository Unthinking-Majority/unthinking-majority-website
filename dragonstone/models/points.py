from datetime import timedelta, datetime

from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from main.models import Settings

__all__ = [
    "DragonstonePoints",
    "FreeformPoints",
    "RecruitmentPoints",
    "SotMPoints",
    "PVMSplitPoints",
    "MentorPoints",
    "EventHostPoints",
    "EventParticipantPoints",
    "EventDonorPoints",
]


class DragonstonePoints(PolymorphicModel):
    account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="dragonstone_points",
    )
    points = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = "Dragonstone Points"
        verbose_name_plural = "Dragonstone Points"

    @classmethod
    def expiration_period(cls):
        return timezone.now().date() - timedelta(
            days=int(Settings.objects.get(name="DRAGONSTONE_EXPIRATION_PERIOD").value)
        )


class FreeformPoints(DragonstonePoints):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)


class RecruitmentPoints(DragonstonePoints):
    recruited = models.ForeignKey("account.Account", on_delete=models.CASCADE)


class SotMPoints(DragonstonePoints):
    rank = models.PositiveIntegerField(choices=((1, "1st"), (2, "2nd"), (3, "3rd")))


class PVMSplitPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.PVMSplitSubmission",
        on_delete=models.CASCADE,
    )


class MentorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.MentorSubmission",
        on_delete=models.CASCADE,
    )


class EventHostPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )


class EventParticipantPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )


class EventDonorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )
