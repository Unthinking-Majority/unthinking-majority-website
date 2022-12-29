from django.urls import path

from account import autocomplete

autocomplete_urlpatterns = [
    path('account-autocomplete/', autocomplete.account_autocomplete, name='account-autocomplete'),
]
