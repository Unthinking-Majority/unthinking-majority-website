from django import forms
from django.contrib.auth.forms import UserCreationForm

from account import models


class CreateAccountForm(UserCreationForm):
    name = forms.CharField(max_length=256, label='In game name')
    email = forms.EmailField(label='Email')

    def save(self, commit=True):
        user = super(CreateAccountForm, self).save(commit)
        user.email = self.cleaned_data['email']
        user.save()
        models.Account.objects.create(
            user=user,
            name=self.cleaned_data['name']
        )
        return user
