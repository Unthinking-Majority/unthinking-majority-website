from django.contrib.admin.utils import prepare_lookup_value
from django.db.models import F
from django.http import JsonResponse
from django.views import View

from main import models


class ContentAutocomplete(View):

    def get(self, request, *args, **kwargs):
        filters = {}
        for key, val in self.request.GET.items():
            filters[key] = prepare_lookup_value(key, val)
        boards = models.Content.objects.filter(**filters).annotate(text=F('name')).values()
        return JsonResponse(list(boards), safe=False)


class PetAutocomplete(View):

    def get(self, request, *args, **kwargs):
        filters = {}
        for key, val in self.request.GET.items():
            filters[key] = prepare_lookup_value(key, val)
        pets = models.Pet.objects.filter(**filters).annotate(text=F('name')).values('id', 'text')
        return JsonResponse(list(pets), safe=False)
