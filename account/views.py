from heapq import merge

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from account import forms
from achievements.models import BaseSubmission
from dragonstone.models import DragonstoneBaseSubmission


class ProfileView(ListView):
    template_name = "account/profile.html"
    paginate_by = 5

    def get_queryset(self):
        # achievements submissions
        achievement_submissions = BaseSubmission.filter_all_submissions_by_account(
            self.request.user.account
        )

        # dragonstone submissions
        dragonstone_submissions = DragonstoneBaseSubmission.objects.filter(
            Q(
                Q(pvmsplitsubmission__accounts=self.request.user.account)
                | Q(mentorsubmission__mentors=self.request.user.account)
                | Q(mentorsubmission__learners=self.request.user.account)
                | Q(eventsubmission__hosts=self.request.user.account)
                | Q(eventsubmission__participants=self.request.user.account)
                | Q(eventsubmission__donors=self.request.user.account)
            )
        )

        return list(
            merge(
                achievement_submissions,
                dragonstone_submissions,
                key=lambda x: (x.date is None, x.date),
                reverse=True,
            )
        )


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
