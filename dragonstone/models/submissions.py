from datetime import datetime

from django.db import models
from django.db.models import F
from polymorphic.models import PolymorphicModel

from dragonstone import EVENT_CHOICES
from dragonstone import managers
from um.functions import get_file_path

__all__ = [
    "DragonstoneBaseSubmission",
    "PVMSplitSubmission",
    "MentorSubmission",
    "EventSubmission",
    "NewMemberRaidSubmission",
]


class DragonstoneBaseSubmission(PolymorphicModel):
    UPLOAD_TO = "dragonstone/submission/proof/"

    proof = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        help_text="Upload an image as proof for this submission.",
    )
    notes = models.TextField(blank=True)
    denial_notes = models.TextField(
        blank=True, help_text="Only fill out if the submission is denied."
    )
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.DragonstoneSubmissionQueryset().as_manager()

    class Meta:
        ordering = [F("date").desc(nulls_last=True)]
        verbose_name = "Dragonstone Base Submission"
        verbose_name_plural = "All Dragonstone Submissions"

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


class PVMSplitSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/pvm/proof/"

    accounts = models.ManyToManyField(
        "account.Account",
        through="dragonstone.PVMSplitPoints",
        related_name="pvm_split_submissions",
    )
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "PVM Split Submission"
        verbose_name_plural = "PVM Split Submissions"

    def type_display(self):
        return "PVM Split Submission"

    def value_display(self):
        accounts = [account.display_name for account in self.accounts.all()]
        return f'{", ".join(accounts)} - {self.content.name}'

    def accounts_display(self):
        return ", ".join([account.display_name for account in self.accounts.all()])


class MentorSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/mentor/proof/"

    learners = models.ManyToManyField(
        "account.Account", related_name="mentor_learner_submissions"
    )
    mentors = models.ManyToManyField(
        "account.Account",
        through="dragonstone.MentorPoints",
        related_name="mentor_mentor_submissions",
    )
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Mentor Submission"
        verbose_name_plural = "Mentor Submissions"

    def type_display(self):
        return "Mentor Submission"

    def value_display(self):
        mentors = [mentor.display_name for mentor in self.mentors.all()]
        return f'Mentorship by {", ".join(mentors)} for {self.content.name}'

    def accounts_display(self):
        return ", ".join([mentor.display_name for mentor in self.mentors.all()])


class EventSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/event/proof/"

    name = models.CharField(max_length=256)
    hosts = models.ManyToManyField(
        "account.Account",
        through="dragonstone.EventHostPoints",
        related_name="event_hosts_submissions",
        blank=True,
    )
    participants = models.ManyToManyField(
        "account.Account",
        through="dragonstone.EventParticipantPoints",
        related_name="event_participants_submissions",
        blank=True,
    )
    donors = models.ManyToManyField(
        "account.Account",
        through="dragonstone.EventDonorPoints",
        related_name="event_donors_submissions",
        blank=True,
    )
    type = models.IntegerField(choices=EVENT_CHOICES)

    class Meta:
        verbose_name = "Event Submission"
        verbose_name_plural = "Event Submissions"

    def type_display(self):
        return "Event Submission"

    def value_display(self):
        return f"{self.name}"

    def accounts_display(self):
        return ", ".join([host.display_name for host in self.hosts.all()])


class NewMemberRaidSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/new_member_raid/proof/"

    accounts = models.ManyToManyField(
        "account.Account",
        through="dragonstone.NewMemberRaidPoints",
        related_name="new_member_raid_submissions",
    )
    new_members = models.ManyToManyField(
        "account.Account", related_name="new_member_raid_new_member_submissions"
    )
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "New Member Raid"
        verbose_name_plural = "New Member Raids"

    def type_display(self):
        return "New Member Raid"

    def value_display(self):
        accounts = [account.display_name for account in self.accounts.all()]
        return f'{", ".join(accounts)} - {self.content.name}'

    def accounts_display(self):
        return ", ".join([account.display_name for account in self.accounts.all()])
