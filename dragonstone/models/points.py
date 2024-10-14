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
from main import EASY, MEDIUM, HARD, VERY_HARD, SKILLS
from main.config import config

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
    "NewMemberRaidPoints",
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
        verbose_name_plural = "All Dragonstone Points"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(DragonstonePoints, self).save(*args, **kwargs)
        if is_new:
            # get_child_instance seems to return self if there is no child. This works out
            # because this code still runs successfully when a child instance is saved!
            self.on_created()

    def on_created(self):
        """
        Post to discord dragonstone updates webhook if a user now qualifies for dragonstone
        because of these points being created
        """
        return self.get_real_instance().on_created()


class FreeformPoints(DragonstonePoints):
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Freeform Points"
        verbose_name_plural = "Freeform Points"

    def on_created(self):
        current_pts = self.account.dragonstone_pts()
        prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
        if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
            self.account.update_dstone_status()


class RecruitmentPoints(DragonstonePoints):
    recruited = models.ForeignKey("account.Account", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Recruitment Points"
        verbose_name_plural = "Recruitment Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            self.points = config.RECRUITER_PTS
        super().save(*args, **kwargs)

    def on_created(self):
        current_pts = self.account.dragonstone_pts()
        prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
        if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
            self.account.update_dstone_status()


class SotMPoints(DragonstonePoints):
    rank = models.PositiveIntegerField(choices=((1, "1st"), (2, "2nd"), (3, "3rd")))
    skill = models.PositiveIntegerField(choices=SKILLS)

    class Meta:
        verbose_name = "Skill of the Month Points"
        verbose_name_plural = "Skill of the Month Points"

    def __str__(self):
        return f"{self.account} - {self.get_rank_display()} place"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.rank == 1:
                self.points = config.SOTM_FIRST_PTS
            elif self.rank == 2:
                self.points = config.SOTM_SECOND_PTS
            elif self.rank == 3:
                self.points = config.SOTM_THIRD_PTS
        super().save(*args, **kwargs)

    def on_created(self):
        current_pts = self.account.dragonstone_pts()
        prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
        if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
            self.account.update_dstone_status()


class PVMSplitPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.PVMSplitSubmission",
        on_delete=models.CASCADE,
        related_name="points",
    )

    class Meta:
        verbose_name = "PVM Split Points"
        verbose_name_plural = "PVM Split Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.content.difficulty == EASY:
                self.points = config.PVM_SPLIT_EASY_PTS
            elif self.submission.content.difficulty == MEDIUM:
                self.points = config.PVM_SPLIT_MEDIUM_PTS
            elif self.submission.content.difficulty == HARD:
                self.points = config.PVM_SPLIT_HARD_PTS
            elif self.submission.content.difficulty == VERY_HARD:
                self.points = config.PVM_SPLIT_VERY_HARD_PTS
            self.date = self.submission.date
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()


class MentorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.MentorSubmission",
        on_delete=models.CASCADE,
        related_name="mentor_points",
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
                self.points = config.MENTOR_VERY_HARD_PTS
            self.date = self.submission.date
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()


class EventHostPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
        related_name="host_points",
    )

    class Meta:
        verbose_name = "Event Host Points"
        verbose_name_plural = "Event Host Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = config.EVENT_MINOR_HOSTS_PTS
            elif self.submission.type == EVENT_MENTOR:
                self.points = config.EVENT_MENTOR_HOSTS_PTS
            elif self.submission.type == MAJOR:
                self.points = config.EVENT_MAJOR_HOSTS_PTS
            elif self.submission.type == OTHER:
                self.points = config.EVENT_OTHER_HOSTS_PTS
        self.date = self.submission.date
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()


class EventParticipantPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
        related_name="participant_points",
    )

    class Meta:
        verbose_name = "Event Participant Points"
        verbose_name_plural = "Event Participant Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = config.EVENT_MINOR_PARTICIPANTS_PTS
            elif self.submission.type == EVENT_MENTOR:
                self.points = config.EVENT_MENTOR_PARTICIPANTS_PTS
            elif self.submission.type == MAJOR:
                self.points = config.EVENT_MAJOR_PARTICIPANTS_PTS
            elif self.submission.type == OTHER:
                self.points = config.EVENT_OTHER_PARTICIPANTS_PTS
        self.date = self.submission.date
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()


class EventDonorPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.EventSubmission",
        on_delete=models.CASCADE,
        related_name="donor_points",
    )

    class Meta:
        verbose_name = "Event Donor Points"
        verbose_name_plural = "Event Donor Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            if self.submission.type == PVM or self.submission.type == SKILLING:
                self.points = config.EVENT_MINOR_DONORS_PTS
            elif self.submission.type == EVENT_MENTOR:
                self.points = config.EVENT_MENTOR_DONORS_PTS
            elif self.submission.type == MAJOR:
                self.points = config.EVENT_MAJOR_DONORS_PTS
            elif self.submission.type == OTHER:
                self.points = config.EVENT_OTHER_DONORS_PTS
            self.date = self.submission.date
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()


class NewMemberRaidPoints(DragonstonePoints):
    submission = models.ForeignKey(
        "dragonstone.NewMemberRaidSubmission",
        on_delete=models.CASCADE,
        related_name="points",
    )

    class Meta:
        verbose_name = "New Member Raid Points"
        verbose_name_plural = "New Member Raid Points"

    def save(self, update_fields=None, *args, **kwargs):
        if not self.pk:
            self.points = config.NEW_MEMBER_RAID_PTS
        super().save(*args, **kwargs)

    def on_created(self):
        """
        Dragonstone rank updates are handled on the parent submission for this type of point.
        Below code handles fringe case of adding more points to a submission in the admin
        after the submission has already been accepted!
        """
        if self.submission.accepted:
            current_pts = self.account.dragonstone_pts()
            prev_pts = self.account.dragonstone_pts(ignore=[self.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                self.account.update_dstone_status()
