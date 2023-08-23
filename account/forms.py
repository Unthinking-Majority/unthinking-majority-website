import random

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from django.urls import reverse_lazy
from django.utils.http import urlencode

from account import models
from main import widgets


class CreateAccountForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    account = forms.ModelChoiceField(queryset=models.Account.objects.all())
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    proof = forms.ImageField(
        help_text="Upload a screenshot of your account with the provided phrase in chat to prove you are the owner of the account."
    )
    phrase = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        if not hasattr(kwargs, "data"):
            kwargs.update(initial={"phrase": self.generate_phrase()})
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields["account"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'user__isnull': True})}",
            placeholder="",
            label="In Game Name",
            help_text="If your in game name is not listed, please contact an admin through discord.",
        )

    @staticmethod
    def generate_phrase():
        adjectives = [
            "scrawny",
            "buff",
            "happy",
            "hungry",
            "spiffy",
            "snobbish",
            "royal",
            "gigantic",
            "small",
            "tiresome",
            "super",
        ]
        nouns = [
            "cat",
            "moose",
            "dog",
            "zebra",
            "hamster",
            "bird",
            "lion",
            "turtle",
            "fish",
            "whale",
            "deer",
            "ant",
            "butterfly",
        ]
        return " ".join([random.choice(l) for l in [adjectives, nouns]])

    def clean_account(self):
        if self.cleaned_data["account"].user:
            raise ValidationError(
                "The account %(ign)s has already been assigned to a user",
                params={"ign": self.cleaned_data["account"].name},
            )
        return self.cleaned_data["account"]

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()

        user_form = UserCreationForm(cleaned_data)
        if not user_form.is_valid():
            raise ValidationError(user_form.errors)

        if models.UserCreationSubmission.objects.filter(
            account=cleaned_data["account"]
        ).exists():
            raise ValidationError(
                f"A submission has already been created for the account {cleaned_data['account']}"
            )

        return cleaned_data

    def form_valid(self):
        models.UserCreationSubmission.objects.create(
            account=self.cleaned_data["account"],
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password1"],
            proof=self.cleaned_data["proof"],
            phrase=self.cleaned_data["phrase"],
        )
