from django.db import models
from django.db.models import Max, Min

from main import CA_DICT
from main.models import PetSubmission, ColLogSubmission, CASubmission


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def pets(self):
        return PetSubmission.objects.accepted().filter(account=self.id)

    def col_logs(self):
        return ColLogSubmission.objects.accepted().filter(account=self.id).aggregate(Max('col_logs'))['col_logs__max'] or 0

    def ca_tier(self):
        ca_tier = CASubmission.objects.accepted().filter(account=self.id).aggregate(Min('ca_tier'))['ca_tier__min']
        return CA_DICT.get(ca_tier, 'None')
