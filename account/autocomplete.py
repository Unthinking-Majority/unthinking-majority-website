from django.contrib.admin.utils import prepare_lookup_value
from django.db.models import F
from django.http import JsonResponse
from django.views import View

from account import models


class AccountAutocomplete(View):

    def get(self, request, *args, **kwargs):
        filters = {}
        for key, val in self.request.GET.items():
            filters[key] = prepare_lookup_value(key, val)
        accounts = models.Account.objects.filter(**filters).annotate(text=F('name')).values('id', 'text')
        return JsonResponse(list(accounts), safe=False)
