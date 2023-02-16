from django.db.models import F
from django.http import JsonResponse
from django.views import View

from account import models


class AccountAutocomplete(View):

    def get(self, request, *args, **kwargs):
        filters = {}
        for key, val in self.request.GET.items():
            filters[key] = val
        accounts = models.Account.objects.filter(**filters).annotate(text=F('name')).values('id', 'text')
        return JsonResponse(list(accounts), safe=False)
