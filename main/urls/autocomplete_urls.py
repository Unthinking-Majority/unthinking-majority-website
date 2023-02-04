from django.urls import path

from main import autocomplete

autocomplete_urlpatterns = [
    path('board-autocomplete/', autocomplete.board_autocomplete, name='board-autocomplete'),
    path('content-autocomplete/', autocomplete.content_autocomplete, name='content-autocomplete'),
    path('pet-autocomplete/', autocomplete.pet_autocomplete, name='pet-autocomplete'),
]
