from django import forms

from main import models


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['account', 'board', 'value', 'proof']
