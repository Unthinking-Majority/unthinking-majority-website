from django import forms
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.http import urlencode

from account.models import Account
from achievements import SUBMISSION_TYPES
from achievements import models as achievements_models
from main import models
from main import widgets


class SelectSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=SUBMISSION_TYPES, coerce=int)


class SelectContentForm(forms.Form):
    content = forms.ModelChoiceField(
        queryset=models.Content.objects.filter(has_pbs=True)
    )

    def __init__(self, *args, **kwargs):
        super(SelectContentForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'has_pbs': True})}",
            placeholder="Select a board",
            label="Board",
        )


class SelectBoardForm(forms.Form):
    board = forms.ModelChoiceField(queryset=models.Board.objects.all())

    def __init__(self, *args, **kwargs):
        content = kwargs.pop("content", None)
        super(SelectBoardForm, self).__init__(*args, **kwargs)
        if content:
            self.fields["board"].queryset = content.boards.all()


class RecordSubmissionForm(forms.ModelForm):
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Talk about gear used, strategy, or even how you felt getting this achievement!"
            }
        ),
    )
    minutes = forms.IntegerField(required=False)
    seconds = forms.DecimalField(required=False)
    value = forms.DecimalField(required=False)
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(), required=False
    )
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False)

    class Meta:
        model = achievements_models.RecordSubmission
        fields = ["board", "accounts", "notes", "value", "proof"]
        widgets = {
            "board": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        board = kwargs.pop("board")

        super(RecordSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["proof"].required = True

        # set board value on form so we can grab it back when it's submitted!
        self.fields["board"].initial = board
        if "account" not in kwargs.get("initial").keys():
            self.fields["account"].widget = widgets.AutocompleteSelectWidget(
                autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
                placeholder="Select account",
                label="Account",
            )
        self.fields["accounts"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all accounts",
            label="Accounts",
        )

    def clean(self):
        cleaned_data = super(RecordSubmissionForm, self).clean()

        # validate value
        if cleaned_data.get("value") is None:
            cleaned_data["value"] = (
                cleaned_data.get("minutes", 0) * 60
            ) + cleaned_data.get("seconds", 0)
            if cleaned_data["value"] <= 0:
                raise forms.ValidationError("Time must be more than 0.")

        # validate team size
        accounts = cleaned_data.get("accounts")
        if accounts and cleaned_data["board"].team_size != accounts.count():
            raise forms.ValidationError(
                "You must select exactly %(team_size)s account(s).",
                params={"team_size": cleaned_data["board"].team_size},
            )

        if cleaned_data["board"].team_size == 1:
            cleaned_data["accounts"] = [cleaned_data["account"]]

        return cleaned_data

    def clean_minutes(self):
        return self.cleaned_data["minutes"] or 0

    def clean_seconds(self):
        return self.cleaned_data["seconds"] or 0.0


class PetSubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    pets = forms.ModelMultipleChoiceField(queryset=models.Pet.objects.all())
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Tell us about this achievement!"}
        ),
    )
    proof = forms.ImageField(required=True)

    def __init__(self, *args, **kwargs):
        super(PetSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["account"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select an account",
            label="Account",
        )
        self.fields["pets"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy("pet-autocomplete"),
            placeholder="Select a pet",
            label="Pet(s)",
        )

    def clean(self):
        cleaned_data = super(PetSubmissionForm, self).clean()

        for pet in cleaned_data["pets"]:
            submission = achievements_models.PetSubmission.objects.accepted().filter(
                Q(account=cleaned_data["account"]),
                Q(pet=pet),
                Q(accepted=None) | Q(accepted=True),
            )
            if submission.exists():
                raise forms.ValidationError(
                    "%(account)s either already owns the pet %(pet)s, or already has a submission under review",
                    params={
                        "account": cleaned_data["account"],
                        "pet": submission.first().pet,
                    },
                )

        return cleaned_data

    def form_valid(self):
        first_submission = achievements_models.PetSubmission.objects.create(
            account=self.cleaned_data["account"],
            pet=self.cleaned_data["pets"][0],
            notes=self.cleaned_data["notes"],
            proof=self.cleaned_data["proof"],
        )
        for pet in self.cleaned_data["pets"][1:]:
            achievements_models.PetSubmission.objects.create(
                account=self.cleaned_data["account"],
                pet=pet,
                notes=self.cleaned_data["notes"],
                proof=first_submission.proof,  # re-use the already uploaded file!
            )


class ColLogSubmissionForm(forms.ModelForm):
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Tell us about this achievement!"}
        ),
    )

    class Meta:
        model = achievements_models.ColLogSubmission
        fields = ["account", "col_logs", "notes", "proof"]

    def __init__(self, *args, **kwargs):
        super(ColLogSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["proof"].required = True

        self.fields["account"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select an account",
            label="Account",
        )

    def clean(self):
        cleaned_data = super(ColLogSubmissionForm, self).clean()

        if cleaned_data.get("col_logs", 0) > settings.MAX_COL_LOG:
            raise forms.ValidationError(
                "You must select a value less than %(max_col_log)s",
                params={"max_col_log": settings.MAX_COL_LOG},
            )

        if cleaned_data["account"].col_logs() >= cleaned_data.get(
            "col_logs", settings.MAX_COL_LOG
        ):
            raise forms.ValidationError(
                "%(account)s already has %(cur_col_logs)s/%(max_col_log)s collection log slots completed.",
                params={
                    "account": cleaned_data["account"],
                    "cur_col_logs": int(cleaned_data["account"].col_logs()),
                    "max_col_log": settings.MAX_COL_LOG,
                },
            )

        return cleaned_data


class CASubmissionForm(forms.ModelForm):
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Tell us about this achievement!"},
        ),
    )

    class Meta:
        model = achievements_models.CASubmission
        fields = ["account", "ca_tier", "notes", "proof"]

    def __init__(self, *args, **kwargs):
        super(CASubmissionForm, self).__init__(*args, **kwargs)

        self.fields["proof"].required = True

        self.fields["account"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select an account",
            label="Account",
        )
