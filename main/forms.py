from django import forms
from django.conf import settings
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


class BoardSubmissionForm(forms.Form):
    notes = forms.CharField(required=False)
    value = forms.DecimalField(required=False)
    minutes = forms.IntegerField(required=False)
    seconds = forms.DecimalField(required=False)
    proof = forms.ImageField()

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

        if not cleaned_data.get('value'):
            cleaned_data['value'] = (cleaned_data.get('minutes', 0) * 60) + cleaned_data.get('seconds', 0)
            if cleaned_data['value'] <= 0:
                raise forms.ValidationError('Time must be more than 0.')

        return cleaned_data

    def clean_minutes(self):
        return self.cleaned_data['minutes'] or 0

    def clean_seconds(self):
        return self.cleaned_data['seconds'] or 0.0


class PetSubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    pets = forms.ModelMultipleChoiceField(queryset=models.Pet.objects.all())
    notes = forms.CharField(required=False)
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(PetSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )
        self.fields['pets'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('pet-autocomplete'),
            placeholder='Select a pet',
            label='Pet(s)',
        )

    def clean(self):
        cleaned_data = super(PetSubmissionForm, self).clean()

        for pet in cleaned_data['pets']:
            submission = models.Submission.objects.accepted().pets().filter(
                accounts=cleaned_data['account'],
                pet=pet
            )
            if submission.exists():
                raise forms.ValidationError(
                    '%(account)s already owns the pet %(pet)s',
                    params={'account': cleaned_data['account'], 'pet': submission.first().pet}
                )

        return cleaned_data


class ColLogSubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    col_logs = forms.IntegerField(max_value=settings.MAX_COL_LOG)
    notes = forms.CharField(required=False)
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(ColLogSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )

    def clean(self):
        cleaned_data = super(ColLogSubmissionForm, self).clean()

        if cleaned_data.get('col_logs', 0) > settings.MAX_COL_LOG:
            raise forms.ValidationError(
                'You must select a value less than %(max_col_log)s',
                params={
                    'max_col_log': settings.MAX_COL_LOG
                }
            )

        if cleaned_data['account'].col_logs >= cleaned_data.get('col_logs', settings.MAX_COL_LOG):
            raise forms.ValidationError(
                '%(account)s already has %(cur_col_logs)s/%(max_col_log)s collection log slots completed.',
                params={
                    'account': cleaned_data['account'],
                    'cur_col_logs': int(cleaned_data['account'].col_logs),
                    'max_col_log': settings.MAX_COL_LOG
                }
            )

        return cleaned_data
