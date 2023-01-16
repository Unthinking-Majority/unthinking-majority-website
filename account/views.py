from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect

from account import forms


class ProfileView(TemplateView):
    template_name = 'account/profile.html'


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