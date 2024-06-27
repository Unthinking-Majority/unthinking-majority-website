from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from bounty import models


class CurrentBountyView(ListView):
    model = models.Bounty
    paginate_by = 10
    template_name = "bounty/bounty.html"

    def dispatch(self, request, *args, **kwargs):
        if not models.Bounty.get_current_bounty():
            return redirect("bounty:index")
        else:
            return super(CurrentBountyView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        bounty = models.Bounty.get_current_bounty()
        submissions = list(bounty.get_submissions())
        slowest_submission = bounty.get_slowest_submission()
        if slowest_submission is not None and slowest_submission not in submissions:
            submissions.append(bounty.get_slowest_submission())
        return submissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bounty = models.Bounty.get_current_bounty()
        context["bounty"] = bounty
        context["content"] = bounty.board.content
        return context


class CurrentBountyRulesView(TemplateView):
    template_name = "bounty/rules.html"

    def dispatch(self, request, *args, **kwargs):
        if not models.Bounty.get_current_bounty():
            return redirect("bounty:index")
        else:
            return super(CurrentBountyRulesView, self).dispatch(
                request, *args, **kwargs
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bounty"] = models.Bounty.get_current_bounty()
        context["bounty_url"] = reverse("bounty:current-bounty")
        return context


class BountyListView(TemplateView):
    template_name = "bounty/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bounties"] = models.Bounty.objects.exclude(
            id=getattr(models.Bounty.get_current_bounty(), "id", None)
        ).order_by("-start_date")
        context["bounty"] = models.Bounty.get_current_bounty()
        return context


class BountyDetail(ListView):
    model = models.Bounty
    template_name = "bounty/detail.html"
    paginate_by = 10

    def get_queryset(self):
        return get_object_or_404(
            models.Bounty, pk=self.kwargs.get("pk")
        ).get_submissions()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bounty = get_object_or_404(models.Bounty, pk=self.kwargs.get("pk"))
        context["bounty"] = bounty
        context["content"] = bounty.board.content
        return context


class BountyRulesDetail(DetailView):
    model = models.Bounty
    template_name = "bounty/rules.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bounty"] = self.object
        context["bounty_url"] = reverse("bounty:detail", kwargs={"pk": self.object.pk})
        return context
