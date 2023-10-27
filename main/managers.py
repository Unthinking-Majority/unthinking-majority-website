from django.db.models import Count, F, Q
from polymorphic.managers import PolymorphicQuerySet


class SubmissionQueryset(PolymorphicQuerySet):
    def accepted(self):
        return self.filter(accepted=True)

    def denied(self):
        return self.filter(accepted=False)

    def active_submissions(self):
        return self.annotate(
            num_accounts=Count("accounts"),
            num_active_accounts=Count("accounts", filter=Q(accounts__is_active=True)),
        ).filter(num_active_accounts__gte=F("num_accounts") / float(2))
