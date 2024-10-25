from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from account import forms
from achievements.models import BaseSubmission
from dragonstone.models import DragonstoneBaseSubmission
from main.config import config


class ProfileView(TemplateView):
    template_name = "account/profile/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        per_page = 5

        achievement_paginator = Paginator(
            BaseSubmission.objects.filter(
                Q(recordsubmission__accounts=self.request.user.account)
                | Q(petsubmission__account=self.request.user.account)
                | Q(collogsubmission__account=self.request.user.account)
                | Q(casubmission__account=self.request.user.account)
            ).distinct(),
            per_page,
        )

        dragonstone_paginator = Paginator(
            DragonstoneBaseSubmission.objects.filter(
                Q(pvmsplitsubmission__accounts=self.request.user.account)
                | Q(mentorsubmission__mentors=self.request.user.account)
                | Q(eventsubmission__hosts=self.request.user.account)
                | Q(eventsubmission__participants=self.request.user.account)
                | Q(eventsubmission__donors=self.request.user.account)
                | Q(newmemberraidsubmission__accounts=self.request.user.account)
                | Q(groupcasubmission__accounts=self.request.user.account)
            ).distinct(),
            per_page,
        )

        data = {
            "achievements": achievement_paginator,
            "dragonstone": dragonstone_paginator,
        }

        if "active_tab" not in self.request.GET.keys():
            context["active_tab"] = "achievements"
        else:
            context["active_tab"] = self.request.GET.get("active_tab")

        active_pb_page = f"{context['active_tab']}_page"
        try:
            context[active_pb_page] = data[context["active_tab"]].page(
                self.request.GET.get("page", 1)
            )
        except EmptyPage:
            context[active_pb_page] = data[context["active_tab"]].page(1)

        context["config"] = config

        return context


class CreateAccountView(FormView):
    template_name = "account/create_account_form.html"
    form_class = forms.CreateAccountForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        form.form_valid()
        messages.success(
            self.request,
            "Account creation form successfully submitted. An admin will review your submission shortly.",
        )
        return super(CreateAccountView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:profile")
        else:
            return super(CreateAccountView, self).dispatch(request, *args, **kwargs)


class ChangePreferredName(FormView):
    template_name = "account/change_preferred_name.html"
    form_class = forms.ChangePreferredNameForm
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        form.set_preferred_name(self.request.user.account)
        messages.success(
            self.request,
            f"Preferred name successfully set to: {self.request.user.account.preferred_name}",
        )
        return super(ChangePreferredName, self).form_valid(form)
