from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from django.urls import reverse_lazy

from account import models
from main import widgets


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=False)

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=commit)
        user.email = self.cleaned_data['email']
        user.save()
        return user


class CreateAccountForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=150,
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    account = forms.ModelChoiceField(
        queryset=models.Account.objects.all()
    )
    email = forms.EmailField(
        label='Email',
        help_text='(Optional) In the event you lose your password, we can use your email to reset it.',
        required=False
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='',
            label='In Game Name',
            help_text='If your in game name is not listed, please contact an admin through discord.',
        )

    def clean_account(self):
        if self.cleaned_data['account'].user:
            raise ValidationError(
                'The account %(ign)s has already been assigned to a user',
                params={
                    'ign': self.cleaned_data['account'].name
                }
            )
        return self.cleaned_data['account']

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()
        user_form = CreateUserForm(cleaned_data)
        if not user_form.is_valid():
            raise ValidationError(user_form.errors)
        return cleaned_data

    def form_valid(self):
        user_form = CreateUserForm(self.cleaned_data)
        user = user_form.save(commit=True)

        account = self.cleaned_data['account']
        account.user = user
        account.save()

        return account
