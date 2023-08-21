from django.urls import path

from main import autocomplete

autocomplete_urlpatterns = [
    path(
        "content-autocomplete/",
        autocomplete.ContentAutocomplete.as_view(),
        name="content-autocomplete",
    ),
    path(
        "pet-autocomplete/",
        autocomplete.PetAutocomplete.as_view(),
        name="pet-autocomplete",
    ),
]
