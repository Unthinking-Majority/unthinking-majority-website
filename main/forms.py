from django import forms
from django.urls import reverse_lazy

from account.models import Account
from main import models
from main import widgets


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['accounts', 'board', 'value', 'proof']
        widgets = {
            'accounts': widgets.AutocompleteSelectWidget(
                autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
                placeholder='Select an account'
            ),
        }

    def __init__(self, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)
