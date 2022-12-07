from admin_auto_filters.filters import AutocompleteFilter


class AccountFilter(AutocompleteFilter):
    title = 'Account'
    field_name = 'account'
