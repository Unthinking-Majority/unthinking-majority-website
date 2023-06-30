from django.shortcuts import render
from django.views.generic.base import TemplateView


class BountyView(TemplateView):
    template_name = 'bounty/bounty.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['bounty']
        return context