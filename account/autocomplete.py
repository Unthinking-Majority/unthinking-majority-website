from dal import autocomplete

from account import models


class AccountAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = models.Account.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
