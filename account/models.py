from django.db import models
from django.db.models import Max, Min

from main.models import Submission
from main import CA_DICT


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def pets(self):
        return Submission.objects.pets().accepted().filter(accounts=self.id)

    def col_logs(self):
        return Submission.objects.col_logs().accepted().filter(accounts=self.id).aggregate(col_logs=Max('value'))['col_logs']

    def ca_tier(self):
        ca_tier = Submission.objects.combat_achievements().accepted().filter(accounts=self.id).aggregate(ca_tier=Min('ca_tier'))['ca_tier']
        return CA_DICT[ca_tier]
