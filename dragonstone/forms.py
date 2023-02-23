from django import forms
from django.urls import reverse_lazy
from django.utils.http import urlencode

from account import DIAMOND
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
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all accounts',
            label='Account',
        )
        self.fields['content'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'can_be_split': True})}",
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
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all mentors',
            label='Mentors',
        )
        self.fields['learners'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all learners',
            label='Learners',
        )
        self.fields['content'].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'can_be_mentored': True})}",
            placeholder='Select content mentored',
            label='Content',
        )


class EventSubmissionForm(forms.ModelForm):

    class Meta:
        model = models.EventSubmission
        fields = ['hosts', 'participants', 'donors', 'type', 'proof', 'notes']

    def __init__(self, *args, **kwargs):
        super(EventSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['hosts'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all hosts',
            label='Hosts',
        )
        self.fields['participants'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all participants',
            label='Participants',
        )
        self.fields['donors'].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True, 'rank__gte': DIAMOND})}",
            placeholder='Select all donors',
            label='Donors',
            required=False
        )
