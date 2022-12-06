from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm

from account import models


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(label='Email')

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=commit)
        user.email = self.cleaned_data['email']
        user.save()
        return user


class CreateAccountForm(forms.ModelForm):
    username = forms.CharField(
        label='Username',
        max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    email = forms.EmailField(
        label='Email',
        help_text='Email address. In the event you lose your password, we can use your email to reset it.'
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text='Enter the same password as before, for verification.',
    )

    class Meta:
        model = models.Account
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean(self):
        return super(CreateAccountForm, self).clean()

    def save(self, commit=True):

        # Create new User using username, password1, password2, email fields
        user = CreateUserForm(self.cleaned_data).save()
        # user.email = self.cleaned_data['email']
        user.save()

        # Create new Account, add above created User object to this newly created Account
        account = super(CreateAccountForm, self).save(commit=commit)
        account.user = user
        account.save()

        return account
