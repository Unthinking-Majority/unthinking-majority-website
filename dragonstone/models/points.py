from datetime import datetime

from django.db import models
from polymorphic.models import PolymorphicModel

from dragonstone import (
    PVM,
    SKILLING,
    MAJOR,
    OTHER,
    EVENT_MENTOR,
)
from dragonstone import managers
from main import EASY, MEDIUM, HARD, VERY_HARD
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

    objects = managers.DragonstonePointsQueryset.as_manager()

    class Meta:
        verbose_name = "Dragonstone Points"
        verbose_name_plural = "Dragonstone Points"


class FreeformPoints(DragonstonePoints):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Freeform Points"
        verbose_name_plural = "Freeform Points"


class RecruitmentPoints(DragonstonePoints):
    recruited = models.ForeignKey("account.Account", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Recruitment Points"
        verbose_name_plural = "Recruitment Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            self.points = int(Settings.objects.get(name="RECRUITER_PTS"))
        super().save(*args, **kwargs)


class SotMPoints(DragonstonePoints):
    rank = models.PositiveIntegerField(choices=((1, "1st"), (2, "2nd"), (3, "3rd")))

    class Meta:
        verbose_name = "Skill of the Month Points"
        verbose_name_plural = "Skill of the Month Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.rank == 1:
                self.points = int(Settings.objects.get(name="SOTM_FIRST_PTS"))
            elif self.rank == 2:
                self.points = int(Settings.objects.get(name="SOTM_SECOND_PTS"))
            elif self.rank == 3:
                self.points = int(Settings.objects.get(name="SOTM_THIRD_PTS"))
        super().save(*args, **kwargs)


class PVMSplitPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.PVMSplitSubmission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "PVM Split Points"
        verbose_name_plural = "PVM Split Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.content__difficulty == EASY:
                self.points = int(
                    Settings.objects.get(name="PVM_SPLITS_EASY_PTS").value
                )
            elif self.submission.content__difficulty == MEDIUM:
                self.points = int(
                    Settings.objects.get(name="PVM_SPLITS_MEDIUM_PTS").value
                )
            elif self.submission.content__difficulty == HARD:
                self.points = int(
                    Settings.objects.get(name="PVM_SPLITS_HARD_PTS").value
                )
            elif self.submission.content__difficulty == VERY_HARD:
                self.points = int(
                    Settings.objects.get(name="PVM_SPLITS_VERY_HARD_PTS").value
                )
            self.date = self.submission.date
        super().save(*args, **kwargs)


class MentorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.MentorSubmission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Mentor Points"
        verbose_name_plural = "Mentor Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.content__difficulty == EASY:
                self.points = int(Settings.objects.get(name="MENTOR_EASY_PTS").value)
            elif self.submission.content__difficulty == MEDIUM:
                self.points = int(Settings.objects.get(name="MENTOR_MEDIUM_PTS").value)
            elif self.submission.content__difficulty == HARD:
                self.points = int(Settings.objects.get(name="MENTOR_HARD_PTS").value)
            elif self.submission.content__difficulty == VERY_HARD:
                self.points = int(
                    Settings.objects.get(name="MENTOR_VERY_HARD_PTS").value
                )
            self.date = self.submission.date
        super().save(*args, **kwargs)


class EventHostPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Event Host Points"
        verbose_name_plural = "Event Host Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = int(
                    Settings.objects.get(name="EVENT_MINOR_HOSTS_PTS").value
                )
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MENTOR_HOSTS_PTS").value
                )
            elif self.submission.type == MAJOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MAJOR_HOSTS_PTS").value
                )
            elif self.submission.type == OTHER:
                self.points = int(
                    Settings.objects.get(name="EVENT_OTHER_HOSTS_PTS").value
                )
        self.date = self.submission.date
        super().save(*args, **kwargs)


class EventParticipantPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Event Participant Points"
        verbose_name_plural = "Event Participant Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = int(
                    Settings.objects.get(name="EVENT_MINOR_PARTICIPANTS_PTS").value
                )
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MENTOR_PARTICIPANTS_PTS").value
                )
            elif self.submission.type == MAJOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MAJOR_PARTICIPANTS_PTS").value
                )
            elif self.submission.type == OTHER:
                self.points = int(
                    Settings.objects.get(name="EVENT_OTHER_PARTICIPANTS_PTS").value
                )
        self.date = self.submission.date
        super().save(*args, **kwargs)


class EventDonorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Event Donor Points"
        verbose_name_plural = "Event Donor Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = int(
                    Settings.objects.get(name="EVENT_MINOR_DONORS_PTS").value
                )
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MENTOR_DONORS_PTS").value
                )
            elif self.submission.type == MAJOR:
                self.points = int(
                    Settings.objects.get(name="EVENT_MAJOR_DONORS_PTS").value
                )
            elif self.submission.type == OTHER:
                self.points = int(
                    Settings.objects.get(name="EVENT_OTHER_DONORS_PTS").value
                )
            self.date = self.submission.date
        super().save(*args, **kwargs)
