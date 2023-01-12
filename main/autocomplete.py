from django.db.models import F
from django.http import JsonResponse

from main import models


def board_autocomplete(request):
    boards = models.Board.objects.annotate(text=F('name')).values()
    return JsonResponse(list(boards), safe=False)


def parent_board_autocomplete(request):
    boards = models.ParentBoard.objects.annotate(text=F('name')).values()
    return JsonResponse(list(boards), safe=False)


def pet_autocomplete(request):
    pets = models.Pet.objects.annotate(text=F('name')).values('id', 'text')
    return JsonResponse(list(pets), safe=False)
