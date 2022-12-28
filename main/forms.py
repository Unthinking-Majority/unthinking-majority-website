from django import forms
from django.urls import reverse_lazy

from account.models import Account
from main import models
from main import widgets


class SelectSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=models.SUBMISSION_TYPES, coerce=int)


class SelectBoardForm(forms.Form):
    board = forms.ModelChoiceField(queryset=models.Board.objects.all())
    team_size = forms.IntegerField(initial=1, min_value=1, max_value=8)

    def __init__(self, *args, **kwargs):
        super(SelectBoardForm, self).__init__(*args, **kwargs)
        self.fields['board'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('board-autocomplete'),
            placeholder='Select a board',
            label='Board',
        )


class BoardSubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['value', 'proof']

    def __init__(self, *args, **kwargs):
        team_size = kwargs.pop('team_size', 1)
        super(BoardSubmissionForm, self).__init__(*args, **kwargs)

        for i in range(team_size):
            self.fields[f'account_{i}'] = forms.ModelChoiceField(queryset=Account.objects.all())
            self.fields[f'account_{i}'].widget = widgets.AutocompleteSelectWidget(
                autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
                placeholder='Select an account',
                label=f'Account {i + 1}',
            )

    def clean(self):
        cleaned_data = super(BoardSubmissionForm, self).clean()
        return cleaned_data


class PetForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    pet = forms.ModelChoiceField(queryset=models.Pet.objects.all())
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(PetForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )
        self.fields['pet'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('pet-autocomplete'),
            placeholder='Select a pet',
            label='Pet',
        )


class CollectionLogForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    collections_logged = forms.IntegerField()
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CollectionLogForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )
