from django.db import models

from main import RECORD, PET, COL_LOG


class SubmissionQueryset(models.query.QuerySet):
    def accepted(self):
        return self.filter(accepted=True)

    def denied(self):
        return self.filter(accepted=False)

    def records(self):
        return self.filter(type=RECORD)

    def pets(self):
        return self.filter(type=PET)

    def col_logs(self):
        return self.filter(type=COL_LOG)
