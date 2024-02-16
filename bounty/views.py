from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from bounty import models


class CurrentBountyView(ListView):
    model = models.Bounty
    paginate_by = 10
    template_name = "bounty/bounty.html"

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        if not models.Bounty.get_current_bounty():
            return redirect("bounty:bounty-index")
        else:
            return super(CurrentBountyView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return models.Bounty.get_current_bounty().get_submissions()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bounty = models.Bounty.get_current_bounty()

        context["bounty"] = bounty
        context["content"] = bounty.board.content

        return context


class BountyIndexView(TemplateView):
    template_name = "bounty/bounty_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bounties"] = models.Bounty.objects.exclude(
            id=getattr(models.Bounty.get_current_bounty(), "id", None)
        ).order_by("-start_date")
        return context


class BountyView(ListView):
    template_name = "bounty/bounty_view.html"
    paginate_by = 10

    def get_queryset(self):
        return get_object_or_404(
            models.Bounty, id=self.kwargs.get("id")
        ).get_submissions()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bounty = get_object_or_404(models.Bounty, id=self.kwargs.get("id"))
        context["bounty"] = bounty
        context["content"] = bounty.board.content
        return context


class BountyRulesView(TemplateView):
    template_name = "bounty/bounty_rules.html"
