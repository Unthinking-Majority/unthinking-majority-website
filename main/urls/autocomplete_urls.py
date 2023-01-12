from django.urls import path

from main import autocomplete

autocomplete_urlpatterns = [
    path('board-autocomplete/', autocomplete.board_autocomplete, name='board-autocomplete'),
    path('parent-board-autocomplete/', autocomplete.parent_board_autocomplete, name='parent-board-autocomplete'),
    path('pet-autocomplete/', autocomplete.pet_autocomplete, name='pet-autocomplete'),
]
