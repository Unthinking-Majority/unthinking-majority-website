from dal import autocomplete
from django import forms

from main import models


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['account', 'board', 'value', 'proof']
        widgets = {
            'account': autocomplete.ModelSelect2(url='accounts:account-autocomplete', attrs={'data-html': True})
        }
