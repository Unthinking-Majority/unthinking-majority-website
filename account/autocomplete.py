from dal import autocomplete

from account.models import Account


class AccountAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Account.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
