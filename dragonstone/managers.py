from datetime import timedelta

from constance import config
from django.db.models import Q
from django.utils import timezone
from polymorphic.managers import PolymorphicQuerySet

from dragonstone import models

__all__ = ["DragonstonePointsQueryset", "DragonstoneSubmissionQueryset"]


class DragonstonePointsQueryset(PolymorphicQuerySet):
    def active(self):
        expiration_period = timezone.now() - timedelta(
            days=config.DRAGONSTONE_EXPIRATION_PERIOD
        )
        return self.filter(
            Q(
                Q(instance_of=models.FreeformPoints)
                | Q(instance_of=models.RecruitmentPoints)
                | Q(instance_of=models.SotMPoints)
                | Q(pvmsplitpoints__submission__accepted=True)
                | Q(mentorpoints__submission__accepted=True)
                | Q(eventhostpoints__submission__accepted=True)
                | Q(eventparticipantpoints__submission__accepted=True)
                | Q(eventdonorpoints__submission__accepted=True)
            )
            & Q(date__gte=expiration_period)
        )


class DragonstoneSubmissionQueryset(PolymorphicQuerySet):
    def accepted(self):
        return self.filter(accepted=True)

    def denied(self):
        return self.filter(accepted=False)

    def active(self):
        expiration_period = timezone.now() - timedelta(
            days=config.DRAGONSTONE_EXPIRATION_PERIOD
        )
        return self.filter(date__gte=expiration_period)
