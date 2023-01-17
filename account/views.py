from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from account import forms
from main.models import Submission


class ProfileView(ListView):
    model = Submission
    template_name = 'account/profile.html'
    paginate_by = 5

    def get_queryset(self):
        return Submission.objects.all().filter(accounts=self.request.user.account)


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