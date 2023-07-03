from django.contrib.postgres.aggregates import StringAgg
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from achievements import models as achievements_models
from bounty import models


class BountyView(ListView):
    model = models.Bounty
    paginate_by = 10
    template_name = "bounty/bounty.html"

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        if not models.Bounty.get_current_bounty():
            return redirect("bounty:bounty-index")
        else:
            return super(BountyView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        bounty = models.Bounty.get_current_bounty()

        ordering = bounty.board.content.ordering

        # annotate the teams (accounts values) into a string so we can order by unique teams of accounts and value
        annotated_submissions = (
            bounty.get_submissions()
            .annotate(
                accounts_str=StringAgg(
                    "accounts__name", delimiter=",", ordering="accounts__name"
                )
            )
            .order_by("accounts_str", f"{ordering}value")
        )

        # grab the first submission for each team (which is the best, since we ordered by value above)
        submissions = {}
        for submission in annotated_submissions:
            if submission.accounts_str not in submissions.keys():
                submissions[submission.accounts_str] = submission.id
        submissions = achievements_models.RecordSubmission.objects.filter(
            id__in=submissions.values()
        ).order_by(f"{ordering}value", "date")

        return submissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bounty = models.Bounty.get_current_bounty()

        context["bounty"] = bounty
        context["content"] = bounty.board.content

        return context


class BountyIndex(TemplateView):
    template_name = "bounty/bounty_index.html"
