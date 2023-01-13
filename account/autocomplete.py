from django.db.models import F
from django.http import JsonResponse

from account import models


def account_autocomplete(request):
    # accounts = models.Account.objects.filter(active=True).annotate(text=F('name')).values('id', 'text')
    accounts = models.Account.objects.annotate(text=F('name')).values('id', 'text')
    return JsonResponse(list(accounts), safe=False)
