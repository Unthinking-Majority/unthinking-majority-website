from django import forms


class AutocompleteSelectWidget(forms.Select):
    autocomplete_url = ''
    placeholder = ''
    label = ''
    template_name = 'main/widgets/autocomplete_select.html'

    def __init__(self, autocomplete_url='', placeholder='', label='', help_text=''):
        self.autocomplete_url = autocomplete_url
        self.placeholder = placeholder
        self.label = label
        self.help_text = help_text
        super(AutocompleteSelectWidget, self).__init__()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['autocomplete_url'] = self.autocomplete_url
        context['placeholder'] = self.placeholder
        context['label'] = self.label
        context['help_text'] = self.help_text
        return context


class AutocompleteSelectMultipleWidget(forms.SelectMultiple):
    autocomplete_url = ''
    placeholder = ''
    label = ''
    template_name = 'main/widgets/autocomplete_select_multiple.html'

    def __init__(self, autocomplete_url='', placeholder='', label=''):
        self.autocomplete_url = autocomplete_url
        self.placeholder = placeholder
        self.label = label
        super(AutocompleteSelectMultipleWidget, self).__init__()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['autocomplete_url'] = self.autocomplete_url
        context['placeholder'] = self.placeholder
        context['label'] = self.label
        return context
