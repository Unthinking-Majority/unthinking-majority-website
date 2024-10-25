import json
from datetime import datetime
from itertools import chain

import requests
from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse
from polymorphic.models import PolymorphicModel

from achievements import CA_CHOICES
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
    "GroupCASubmission",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_accepted = self.accepted

    def save(self, *args, **kwargs):
        super(DragonstoneBaseSubmission, self).save(*args, **kwargs)
        if self.accepted and self.accepted != self.__original_accepted:
            # get_child_instance seems to return self if there is no child. This works out
            # because this code still runs successfully when a child instance is saved!
            self.on_accepted()

    def on_creation(self):
        """
        Post to discord dragonstone submission webhook the newly created submission
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

    def on_accepted(self):
        """
        Post to discord dragonstone updates webhook if a user now qualifies for dragonstone
        because of this submission being accepted
        """
        return self.get_real_instance().on_accepted()

    def create_new_submission_embed(self):
        return self.get_real_instance().create_new_submission_embed()

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

    def on_accepted(self):
        for pt in self.points.all():
            current_pts = pt.account.get_dragonstone_pts()
            prev_pts = pt.account.get_dragonstone_pts(ignore=[pt.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                pt.account.notify_dstone_status_change()


class MentorSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/mentor/proof/"

    learners = models.ManyToManyField(
        "account.Account", related_name="mentor_learner_submissions", blank=True
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

    def on_accepted(self):
        for pt in self.mentor_points.all():
            current_pts = pt.account.get_dragonstone_pts()
            prev_pts = pt.account.get_dragonstone_pts(ignore=[pt.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                pt.account.notify_dstone_status_change()


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

    def on_accepted(self):
        from account.models import Account

        host_points = self.host_points.all()
        participant_points = self.participant_points.all()
        donor_points = self.donor_points.all()
        accounts_pks = list(
            chain(
                host_points.values_list("account", flat=True),
                participant_points.values_list("account", flat=True),
                donor_points.values_list("account", flat=True),
            )
        )
        accounts = Account.objects.filter(pk__in=accounts_pks)
        for account in accounts:
            current_pts = account.get_dragonstone_pts()
            ignore = []
            if account.pk in host_points.values_list("account", flat=True):
                ignore.append(host_points.get(account=account).pk)
            if account.pk in participant_points.values_list("account", flat=True):
                ignore.append(participant_points.get(account=account).pk)
            if account.pk in donor_points.values_list("account", flat=True):
                ignore.append(donor_points.get(account=account).pk)
            prev_pts = account.get_dragonstone_pts(ignore=ignore)
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                account.notify_dstone_status_change()


class NewMemberRaidSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/new_member_raid/proof/"

    accounts = models.ManyToManyField(
        "account.Account",
        through="dragonstone.NewMemberRaidPoints",
        related_name="new_member_raid_submissions",
    )
    new_members = models.ManyToManyField(
        "account.Account",
        related_name="new_member_raid_new_member_submissions",
        blank=True,
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

    def on_accepted(self):
        for pt in self.points.all():
            current_pts = pt.account.get_dragonstone_pts()
            prev_pts = pt.account.get_dragonstone_pts(ignore=[pt.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                pt.account.notify_dstone_status_change()


class GroupCASubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/group_ca/proof/"

    accounts = models.ManyToManyField(
        "account.Account",
        through="dragonstone.GroupCAPoints",
        related_name="group_ca_submissions",
    )
    ca_tier = models.IntegerField(
        choices=CA_CHOICES,
        verbose_name="Combat Achievement Tier",
    )
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Group CA Submission"
        verbose_name_plural = "Group CA Submissions"

    def create_new_submission_embed(self):
        """
        Create json discord embed for newly created Group CA submissions.
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
        return "Group CA Submission"

    def value_display(self):
        accounts = [account.display_name for account in self.accounts.all()]
        return f'{", ".join(accounts)} - {self.content.name}'

    def accounts_display(self):
        return ", ".join([account.display_name for account in self.accounts.all()])

    def on_accepted(self):
        for pt in self.points.all():
            current_pts = pt.account.get_dragonstone_pts()
            prev_pts = pt.account.get_dragonstone_pts(ignore=[pt.pk])
            if current_pts >= config.DRAGONSTONE_POINTS_THRESHOLD > prev_pts:
                pt.account.notify_dstone_status_change()
