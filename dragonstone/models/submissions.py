import json
from datetime import datetime

import requests
from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse
from polymorphic.models import PolymorphicModel

from dragonstone import EVENT_CHOICES
from dragonstone import managers
from main.config import config
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
        if config.UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL:
            requests.post(
                config.UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
            )

    def create_new_submission_embed(self):
        return self.get_real_instanc().create_new_submission_embed()

    def create_new_submission_components(self):
        components = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "label": "Accept",
                        "style": 3,
                        "custom_id": f"dragonstone-accept-submission-{self.pk}",
                    },
                    {
                        "type": 2,
                        "label": "Deny",
                        "style": 4,
                        "custom_id": f"dragonstone-deny-submission-{self.pk}",
                    },
                ],
            }
        ]
        return components

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

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created PVM split submissions.
        """
        fields = [
            {
                "name": "Type",
                "value": self.type_display(),
                "inline": True,
            },
            {
                "name": "Content",
                "value": self.content.name,
                "inline": True,
            },
            {
                "name": "Account(s)",
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
            "title": "New Dragonstone Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{admin_url}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed

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

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created mentor submissions.
        """
        fields = [
            {
                "name": "Type",
                "value": self.type_display(),
                "inline": True,
            },
            {
                "name": "Content",
                "value": self.content.name,
                "inline": True,
            },
            {
                "name": "Mentor(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.mentors.all()]
                ),
            },
            {
                "name": "Learner(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.learners.all()]
                ),
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
            "title": "New Dragonstone Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{admin_url}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed

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

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created event submissions.
        """
        fields = [
            {
                "name": "Type",
                "value": self.type_display(),
                "inline": True,
            },
            {
                "name": "Event Type",
                "value": self.get_type_display(),
                "inline": True,
            },
            {
                "name": "Hosts(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.hosts.all()]
                ),
            },
            {
                "name": "Participant(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.participants.all()]
                ),
            },
            {
                "name": "Donor(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.donors.all()]
                ),
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
            "title": "New Dragonstone Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{admin_url}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed

    def type_display(self):
        return "Event Submission"

    def value_display(self):
        return f"{self.name}"

    def accounts_display(self):
        return ", ".join([host.display_name for host in self.hosts.all()])

    def roles_display(self, account):
        """
        Display the role(s) the passed account played in this submission.
        """
        roles = []
        if account in self.hosts.all():
            roles += ["Host"]
        if account in self.participants.all():
            roles += ["Participant"]
        if account in self.donors.all():
            roles += ["Donor"]
        return ", ".join(roles)


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

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created new member raid submissions.
        """
        fields = [
            {
                "name": "Type",
                "value": self.type_display(),
                "inline": True,
            },
            {
                "name": "Content",
                "value": self.content.name,
                "inline": True,
            },
            {
                "name": "Account(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.accounts.all()]
                ),
            },
            {
                "name": "New Member(s)",
                "value": ", ".join(
                    [mentor.display_name for mentor in self.new_members.all()]
                ),
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
            "title": "New Dragonstone Submission",
            "fields": fields,
            "url": f"https://{settings.DOMAIN}{admin_url}",
        }

        if not settings.DEBUG and self.proof:
            embed["image"] = {"url": self.proof.url}

        return embed

    def type_display(self):
        return "New Member Raid"

    def value_display(self):
        accounts = [account.display_name for account in self.accounts.all()]
        return f'{", ".join(accounts)} - {self.content.name}'

    def accounts_display(self):
        return ", ".join([account.display_name for account in self.accounts.all()])
