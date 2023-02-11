from django.db import models

from main import RECORD, PET, COL_LOG, CA


class SubmissionQueryset(models.query.QuerySet):
    def accepted(self):
        return self.filter(accepted=True)

    def denied(self):
        return self.filter(accepted=False)
