from django import forms
from django.urls import reverse_lazy

from main import models
from main import widgets


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['account', 'board', 'value', 'proof']
        widgets = {
            'account': widgets.AutocompleteSelectWidget(
                autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
                placeholder='Select an account'
            )
        }
