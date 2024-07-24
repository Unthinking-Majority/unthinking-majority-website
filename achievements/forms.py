from django import forms
from django.conf import settings
from django.db.models import Q
from django.forms import ValidationError
from django.urls import reverse_lazy
from django.utils.http import urlencode

from account.models import Account
from achievements import SUBMISSION_TYPES
from achievements import models
from bounty.models import Bounty
from main import models as main_models
from main import widgets


class SelectSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=SUBMISSION_TYPES, coerce=int)


class SelectContentForm(forms.Form):
    content = forms.ModelChoiceField(
        queryset=main_models.Content.objects.filter(has_pbs=True)
    )

    def __init__(self, *args, **kwargs):
        super(SelectContentForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'has_pbs': True})}",
            placeholder="Select a board",
            label="Board",
        )


class SelectBoardForm(forms.Form):
    board = forms.ModelChoiceField(queryset=main_models.Board.objects.all())

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
        model = models.RecordSubmission
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

        accounts = cleaned_data.get("accounts")

        # validate team size
        if accounts and cleaned_data["board"].team_size != accounts.count():
            raise forms.ValidationError(
                "You must select exactly %(team_size)s account(s).",
                params={"team_size": cleaned_data["board"].team_size},
            )

        # validate all accounts are active for team submissions
        if accounts.filter(is_active=False).exists():
            raise forms.ValidationError(
                "The following account(s) are currently not in the clan: %(inactive_accounts)s",
                params={
                    "inactive_accounts": ",".join(
                        accounts.filter(is_active=False).values_list(
                            "display_name", flat=True
                        )
                    )
                },
            )

        # validate account is active if solo submission
        if (
            cleaned_data["board"].team_size == 1
            and cleaned_data["account"].is_active is False
        ):
            raise forms.ValidationError(
                "The account %(account)s is not a current member of the clan.",
                params={"account": cleaned_data["account"].display_name},
            )

        # For solo submissions, copy account field into array variable accounts to fit into RecordSubmission model
        if cleaned_data["board"].team_size == 1:
            cleaned_data["accounts"] = [cleaned_data["account"]]

        return cleaned_data

    def clean_minutes(self):
        return self.cleaned_data["minutes"] or 0

    def clean_seconds(self):
        return self.cleaned_data["seconds"] or 0.0


class PetSubmissionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all())
    pets = forms.ModelMultipleChoiceField(queryset=main_models.Pet.objects.all())
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Tell us about this achievement!"}
        ),
    )
    proof = forms.ImageField(required=True)

    def __init__(self, *args, **kwargs):
        super(PetSubmissionForm, self).__init__(*args, **kwargs)

        if "account" not in kwargs.get("initial").keys():
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

        if not cleaned_data.get("account").is_active:
            raise forms.ValidationError(
                "The account %(account)s is not a current member of the clan.",
                params={"account": cleaned_data.get("account").display_name},
            )

        for pet in cleaned_data["pets"]:
            submission = models.PetSubmission.objects.accepted().filter(
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
        submissions = []
        first_submission = models.PetSubmission.objects.create(
            account=self.cleaned_data["account"],
            pet=self.cleaned_data["pets"][0],
            notes=self.cleaned_data["notes"],
            proof=self.cleaned_data["proof"],
        )
        submissions.append(first_submission)
        for pet in self.cleaned_data["pets"][1:]:
            submission = models.PetSubmission.objects.create(
                account=self.cleaned_data["account"],
                pet=pet,
                notes=self.cleaned_data["notes"],
                proof=first_submission.proof,  # re-use the already uploaded file!
            )
            submissions.append(submission)
        return submissions


class ColLogSubmissionForm(forms.ModelForm):
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Tell us about this achievement!"}
        ),
    )

    class Meta:
        model = models.ColLogSubmission
        fields = ["account", "col_logs", "notes", "proof"]

    def __init__(self, *args, **kwargs):
        super(ColLogSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["proof"].required = True

        if "account" not in kwargs.get("initial").keys():
            self.fields["account"].widget = widgets.AutocompleteSelectWidget(
                autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
                placeholder="Select an account",
                label="Account",
            )

    def clean(self):
        cleaned_data = super(ColLogSubmissionForm, self).clean()

        if not cleaned_data.get("account").is_active:
            raise forms.ValidationError(
                "The account %(account)s is not a current member of the clan.",
                params={"account": cleaned_data.get("account").display_name},
            )

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
        model = models.CASubmission
        fields = ["account", "ca_tier", "notes", "proof"]

    def __init__(self, *args, **kwargs):
        super(CASubmissionForm, self).__init__(*args, **kwargs)

        self.fields["proof"].required = True

        if "account" not in kwargs.get("initial").keys():
            self.fields["account"].widget = widgets.AutocompleteSelectWidget(
                autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
                placeholder="Select an account",
                label="Account",
            )

    def clean(self):
        cleaned_data = super(CASubmissionForm, self).clean()

        if not cleaned_data.get("account").is_active:
            raise forms.ValidationError(
                "The account %(account)s is not a current member of the clan.",
                params={"account": cleaned_data.get("account").display_name},
            )

        return cleaned_data


class RecordSubmissionAdminForm(forms.ModelForm):
    class Meta:
        model = models.RecordSubmission
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        bounty = Bounty.get_current_bounty()

        if bounty and bounty.board == cleaned_data["board"]:
            if (
                cleaned_data["bounty_accepted"] is None
                and cleaned_data["accepted"] is not None
            ):
                raise ValidationError(
                    f"You must specify whether this submission is accepted for the current bounty or not"
                )
        return cleaned_data


class RecordSubmissionChangelistAdminForm(forms.BaseModelFormSet):
    def clean(self):
        form_sets = self.cleaned_data
        bounty = Bounty.get_current_bounty()
        for cleaned_data in form_sets:
            if bounty and bounty.board == cleaned_data["basesubmission_ptr"].board:
                if (
                    cleaned_data["bounty_accepted"] is None
                    and cleaned_data["accepted"] is not None
                ):
                    raise ValidationError(
                        f"You must specify whether a submission a part of a current bounty is accepted for the bounty or not."
                    )
        return form_sets
