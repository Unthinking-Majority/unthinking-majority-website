from django import forms
from django.urls import reverse_lazy

from dragonstone import DRAGONSTONE_SUBMISSION_TYPES
from dragonstone import models
from main import widgets


class SelectDragonstoneSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=DRAGONSTONE_SUBMISSION_TYPES, coerce=int)


class PVMSplitSubmissionForm(forms.ModelForm):

    class Meta:
        model = models.PVMSplitSubmission
        fields = ['accounts', 'content', 'proof', 'notes']

    def __init__(self, *args, **kwargs):
        super(PVMSplitSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['accounts'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all accounts',
            label='Account',
        )
        self.fields['content'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('content-autocomplete'),
            placeholder='Select content',
            label='Content',
        )


class MentorSubmissionForm(forms.ModelForm):

    class Meta:
        model = models.MentorSubmission
        fields = ['mentors', 'learners', 'content', 'proof', 'notes']

    def __init__(self, *args, **kwargs):
        super(MentorSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['mentors'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all mentors',
            label='Mentors',
        )
        self.fields['learners'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all learners',
            label='Learners',
        )
        self.fields['content'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=reverse_lazy('content-autocomplete'),
            placeholder='Select content mentored',
            label='Content',
        )


class EventSubmissionForm(forms.ModelForm):

    class Meta:
        model = models.EventSubmission
        fields = ['hosts', 'participants', 'donators', 'type', 'proof', 'notes']

    def __init__(self, *args, **kwargs):
        super(EventSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['hosts'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all hosts',
            label='Hosts',
        )
        self.fields['participants'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all participants',
            label='Participants',
        )
        self.fields['donators'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=reverse_lazy('accounts:account-autocomplete'),
            placeholder='Select all donators',
            label='Donators',
        )
