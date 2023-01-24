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


class ParentBoardFilter(AutocompleteFilter):
    title = 'Parent Board'
    field_name = 'parent'


class PetFilter(AutocompleteFilter):
    title = 'Pet'
    field_name = 'pet'
