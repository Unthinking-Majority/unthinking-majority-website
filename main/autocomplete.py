from dal import autocomplete

from main import models


class BoardAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = models.Board.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class PetAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = models.Pet.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
