from admin_auto_filters.filters import AutocompleteFilter


class AccountFilter(AutocompleteFilter):
    title = 'Account'
    field_name = 'account'


class AccountsFilter(AutocompleteFilter):
    title = 'Account'
    field_name = 'accounts'


class BoardFilter(AutocompleteFilter):
    title = 'Board'
    field_name = 'board'


class ContentFilter(AutocompleteFilter):
    title = 'Content'
    field_name = 'content'


class PetFilter(AutocompleteFilter):
    title = 'Pet'
    field_name = 'pet'
