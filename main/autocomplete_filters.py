from admin_auto_filters.filters import AutocompleteFilter


class AccountFilter(AutocompleteFilter):
    title = 'Account'
    field_name = 'account'


class BoardCategoryFilter(AutocompleteFilter):
    title = 'Category'
    field_name = 'category'


class PetFilter(AutocompleteFilter):
    title = 'Pet'
    field_name = 'pet'
