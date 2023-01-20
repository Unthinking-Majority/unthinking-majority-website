from django import forms
from django.conf import settings
from django.urls import reverse_lazy

from account.models import Account
from main import CA_CHOICES
from main import models
from main import widgets


class SelectSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=models.SUBMISSION_TYPES, coerce=int)


class SelectParentBoardForm(forms.Form):
    parent_board = forms.ModelChoiceField(queryset=models.ParentBoard.objects.all())

    def __init__(self, *args, **kwargs):
        super(SelectParentBoardForm, self).__init__(*args, **kwargs)
        self.fields['parent_board'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('parent-board-autocomplete'),
            placeholder='Select a board',
            label='Board',
        )


class SelectBoardForm(forms.Form):
    board = forms.ModelChoiceField(queryset=models.Board.objects.all())

    def __init__(self, *args, **kwargs):
        parent_board = kwargs.pop('parent_board', None)
        super(SelectBoardForm, self).__init__(*args, **kwargs)
        if parent_board:
            self.fields['board'].queryset = parent_board.boards.all()


class BoardSubmissionForm(forms.Form):
    board = forms.ModelChoiceField(queryset=models.Board.objects.all(), widget=forms.HiddenInput())
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all())
    notes = forms.CharField(required=False)
    value = forms.DecimalField(max_digits=7, decimal_places=2, min_value=0, required=False)
    minutes = forms.IntegerField(required=False)
    seconds = forms.DecimalField(required=False)
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board')

        super(BoardSubmissionForm, self).__init__(*args, **kwargs)

        self.fields['board'].initial = board
        self.fields['accounts'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all accounts',
            label='Accounts',
        )

    def clean(self):
        cleaned_data = super(BoardSubmissionForm, self).clean()

        # validate value
        if cleaned_data.get('value') is None:
            cleaned_data['value'] = (cleaned_data.get('minutes', 0) * 60) + cleaned_data.get('seconds', 0)
            if cleaned_data['value'] <= 0:
                raise forms.ValidationError('Time must be more than 0.')

        # validate team size
        accounts = cleaned_data.get('accounts')
        if accounts and cleaned_data['board'].team_size != accounts.count():
            raise forms.ValidationError(
                'You must select exactly %(team_size)s account(s).',
                params={
                    'team_size': cleaned_data['board'].team_size
                }
            )
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
            submission = models.Submission.objects.pets().filter(
                accounts=cleaned_data['account'],
                pet=pet,
                accepted=None
            )
            if submission.exists():
                raise forms.ValidationError(
                    '%(account)s already has a submission for the pet %(pet)s under review',
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

        if cleaned_data['account'].col_logs() >= cleaned_data.get('col_logs', settings.MAX_COL_LOG):
            raise forms.ValidationError(
                '%(account)s already has %(cur_col_logs)s/%(max_col_log)s collection log slots completed.',
                params={
                    'account': cleaned_data['account'],
                    'cur_col_logs': int(cleaned_data['account'].col_logs()),
                    'max_col_log': settings.MAX_COL_LOG
                }
            )

        return cleaned_data


class CASubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    ca_tier = forms.TypedChoiceField(choices=CA_CHOICES, coerce=int)
    notes = forms.CharField(required=False)
    proof = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CASubmissionForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select an account',
            label='Account',
        )
