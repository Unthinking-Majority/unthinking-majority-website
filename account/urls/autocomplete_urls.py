from django.urls import path

from account import autocomplete

autocomplete_urlpatterns = [
    path('account-autocomplete/', autocomplete.AccountAutocomplete.as_view(), name='account-autocomplete'),
]
