from django.db import models


class SubmissionManger(models.Manager):
    def accepted(self):
        return self.filter(accepted=True)
