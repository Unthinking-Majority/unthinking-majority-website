from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.db.models import Q

from account import forms
from achievements.models import BaseSubmission, RecordSubmission, PetSubmission, ColLogSubmission, CASubmission


class ProfileView(ListView):
    template_name = 'account/profile.html'
    paginate_by = 5

    def get_queryset(self):
        record_submissions = RecordSubmission.objects.filter(accounts=self.request.user.account).values('pk')
        pet_submissions = PetSubmission.objects.filter(account=self.request.user.account).values('pk')
        col_logs_submissions = ColLogSubmission.objects.filter(account=self.request.user.account).values('pk')
        ca_submissions = CASubmission.objects.filter(account=self.request.user.account).values('pk')

        submissions = BaseSubmission.objects.filter(
            Q(pk__in=record_submissions) |
            Q(pk__in=pet_submissions) |
            Q(pk__in=col_logs_submissions) |
            Q(pk__in=ca_submissions)
        )

        return [obj.get_child_instance() for obj in submissions]


class CreateAccountView(FormView):
    template_name = 'account/create_account_form.html'
    form_class = forms.CreateAccountForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        form.form_valid()
        return super(CreateAccountView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        else:
            return super(CreateAccountView, self).dispatch(request, *args, **kwargs)