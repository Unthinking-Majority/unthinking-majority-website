from datetime import datetime

from constance import config
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
            self.points = config.RECRUITER_PTS
        super().save(*args, **kwargs)


class SotMPoints(DragonstonePoints):
    rank = models.PositiveIntegerField(choices=((1, "1st"), (2, "2nd"), (3, "3rd")))

    class Meta:
        verbose_name = "Skill of the Month Points"
        verbose_name_plural = "Skill of the Month Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.rank == 1:
                self.points = config.SOTM_FIRST_PTS
            elif self.rank == 2:
                self.points = config.SOTM_SECOND_PTS
            elif self.rank == 3:
                self.points = config.SOTM_THIRD_PTS
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
            if self.submission.content.difficulty == EASY:
                self.points = int(config.PVM_SPLITS_EASY_PTS)
            elif self.submission.content.difficulty == MEDIUM:
                self.points = int(config.PVM_SPLITS_MEDIUM_PTS)
            elif self.submission.content.difficulty == HARD:
                self.points = int(config.PVM_SPLITS_HARD_PTS)
            elif self.submission.content.difficulty == VERY_HARD:
                self.points = int(config.PVM_SPLITS_VERY_HARD_PTS)
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
            if self.submission.content.difficulty == EASY:
                self.points = config.MENTOR_EASY_PTS
            elif self.submission.content.difficulty == MEDIUM:
                self.points = config.MENTOR_MEDIUM_PTS
            elif self.submission.content.difficulty == HARD:
                self.points = config.MENTOR_HARD_PTS
            elif self.submission.content.difficulty == VERY_HARD:
                self.points = int(config.MENTOR_VERY_HARD_PTS)
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
                self.points = int()
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(config.EVENT_MENTOR_HOSTS_PTS)
            elif self.submission.type == MAJOR:
                self.points = int(config.EVENT_MAJOR_HOSTS_PTS)
            elif self.submission.type == OTHER:
                self.points = int(config.EVENT_OTHER_HOSTS_PTS)
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
                self.points = int(config.EVENT_MINOR_PARTICIPANTS_PTS)
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(config.EVENT_MENTOR_PARTICIPANTS_PTS)
            elif self.submission.type == MAJOR:
                self.points = int(config.EVENT_MAJOR_PARTICIPANTS_PTS)
            elif self.submission.type == OTHER:
                self.points = int(config.EVENT_OTHER_PARTICIPANTS_PTS)
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
                self.points = int(config.EVENT_MINOR_DONORS_PTS)
            elif self.submission.type == EVENT_MENTOR:
                self.points = int(config.EVENT_MENTOR_DONORS_PTS)
            elif self.submission.type == MAJOR:
                self.points = int(config.EVENT_MAJOR_DONORS_PTS)
            elif self.submission.type == OTHER:
                self.points = int(config.EVENT_OTHER_DONORS_PTS)
            self.date = self.submission.date
        super().save(*args, **kwargs)
