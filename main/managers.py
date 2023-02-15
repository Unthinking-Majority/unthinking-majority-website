from django.db import models


class SubmissionQueryset(models.query.QuerySet):
    def accepted(self):
        return self.filter(accepted=True)

    def denied(self):
        return self.filter(accepted=False)
