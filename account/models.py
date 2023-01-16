from django.db import models

from main.models import Submission


class Account(models.Model):
    GRANDMASTER, MASTER, ELITE = range(3)
    CA_CHOICES = (
        (GRANDMASTER, 'GrandMaster'),
        (MASTER, 'Master'),
        (ELITE, 'Elite'),
    )
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)
    active = models.BooleanField(default=True)
    col_logs = models.PositiveIntegerField(default=0)
    combat_achievement_tier = models.IntegerField(choices=CA_CHOICES, default=None, null=True, blank=True)

    def __str__(self):
        return self.name

    def pets(self):
        return Submission.objects.accepted().pets().filter(accounts=self.pk)
