from django.db import models
from django.db.models import Max, Min

from account import ACCOUNT_RANK_CHOICES
from achievements import CA_DICT
from achievements.models import PetSubmission, ColLogSubmission, CASubmission
from dragonstone.models import RecruitmentSubmission, SotMSubmission, PVMSplitSubmission, MentorSubmission, EventSubmission


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)
    is_active = models.BooleanField(default=True)
    rank = models.PositiveIntegerField(choices=ACCOUNT_RANK_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name

    def pets(self):
        return PetSubmission.objects.accepted().filter(account=self.id)

    def col_logs(self):
        return ColLogSubmission.objects.accepted().filter(account=self.id).aggregate(Max('col_logs'))['col_logs__max'] or 0

    def ca_tier(self):
        ca_tier = CASubmission.objects.accepted().filter(account=self.id).aggregate(Min('ca_tier'))['ca_tier__min']
        return CA_DICT.get(ca_tier, 'None')

    def dragonstone_pts(self):
        recruitment_pts = RecruitmentSubmission.annotate_dragonstone_pts(account=self)
        sotm_pts = SotMSubmission.annotate_dragonstone_pts(account=self)
        pvm_splits_pts = PVMSplitSubmission.annotate_dragonstone_pts(account=self)
        mentor_pts = MentorSubmission.annotate_dragonstone_pts(account=self)
        event_pts = EventSubmission.annotate_dragonstone_pts(account=self)
        return recruitment_pts + sotm_pts + pvm_splits_pts + mentor_pts + event_pts

