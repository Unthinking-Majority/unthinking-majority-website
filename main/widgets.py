from django import forms


class AutocompleteSelectWidget(forms.Select):
    autocomplete_url = ''
    placeholder = ''
    template_name = 'widgets/autocomplete_select.html'

    def __init__(self, autocomplete_url='', placeholder=''):
        self.autocomplete_url = autocomplete_url
        self.placeholder = placeholder
        super(AutocompleteSelectWidget, self).__init__()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['autocomplete_url'] = self.autocomplete_url
        context['placeholder'] = self.placeholder
        return context
