from django import forms
from django.conf import settings
from django.db.models import Max
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

    def clean(self):
        cleaned_data = super(SelectBoardForm, self).clean()
        if cleaned_data['team_size'] > cleaned_data['board'].max_team_size:
            raise forms.ValidationError(
                'Invalid team size of %(team_size)s selected',
                params={'team_size': cleaned_data['team_size']}
            )
        return cleaned_data


class BoardSubmissionForm(forms.ModelForm):
    class Meta:
        model = models.Submission
        fields = ['value', 'proof', 'notes']

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
    notes = forms.CharField()
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

    def clean(self):
        cleaned_data = super(PetForm, self).clean()

        submission = models.Submission.objects.accepted().pets().filter(
            accounts=cleaned_data['account'],
            pet=cleaned_data['pet']
        )
        if submission.exists():
            raise forms.ValidationError(
                '%(account)s already owns the pet %(pet)s',
                params={'account': cleaned_data['account'], 'pet': submission.first().pet}
            )

        return cleaned_data


class CollectionLogForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    col_logs = forms.IntegerField()
    notes = forms.CharField()
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CollectionLogForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )

    def clean(self):
        cleaned_data = super(CollectionLogForm, self).clean()

        if cleaned_data['account'].col_logs >= cleaned_data['col_logs']:
            raise forms.ValidationError(
                '%(account)s already has %(cur_col_logs)s/%(max_col_log)s collection log slots completed.',
                params={
                    'account': cleaned_data['account'],
                    'cur_col_logs': int(cleaned_data['account'].col_logs),
                    'max_col_log': settings.MAX_COL_LOG
                }
            )

        return cleaned_data
