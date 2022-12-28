from django.db import models

from main.models import Submission


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=256, help_text='In game name.', unique=True)

    def __str__(self):
        return self.name

    def pets(self):
        return Submission.objects.accepted().pets().filter(accounts=self.pk)
