from django.db.models import F
from django.http import JsonResponse

from account import models


def account_autocomplete(request):
    pets = models.Account.objects.annotate(text=F('name')).values('id', 'text')
    return JsonResponse(list(pets), safe=False)
