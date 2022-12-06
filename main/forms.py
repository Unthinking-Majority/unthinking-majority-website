from django import forms

from main.models import Board
from account.models import Account


class SubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    board = forms.ModelChoiceField(queryset=Board.objects.all())
    value = forms.DecimalField(max_digits=6, decimal_places=2)
    proof = forms.ImageField()
