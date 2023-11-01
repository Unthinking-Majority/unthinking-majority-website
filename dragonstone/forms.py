from django import forms
from django.urls import reverse_lazy
from django.utils.http import urlencode

from dragonstone import DRAGONSTONE_SUBMISSION_TYPES
from dragonstone import models
from main import widgets


class SelectDragonstoneSubmissionTypeForm(forms.Form):
    type = forms.TypedChoiceField(choices=DRAGONSTONE_SUBMISSION_TYPES, coerce=int)


class PVMSplitSubmissionForm(forms.ModelForm):
    class Meta:
        model = models.PVMSplitSubmission
        fields = ["accounts", "content", "proof", "notes"]

    def __init__(self, *args, **kwargs):
        super(PVMSplitSubmissionForm, self).__init__(*args, **kwargs)
        self.fields["accounts"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all accounts",
            label="Account",
        )
        self.fields["content"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'can_be_split': True})}",
            placeholder="Select content",
            label="Content",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        def save_m2m():
            for account in self.cleaned_data["accounts"]:
                models.PVMSplitPoints.objects.create(
                    account=account,
                    submission=instance,
                )

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class MentorSubmissionForm(forms.ModelForm):
    class Meta:
        model = models.MentorSubmission
        fields = ["mentors", "learners", "content", "proof", "notes"]

    def __init__(self, *args, **kwargs):
        super(MentorSubmissionForm, self).__init__(*args, **kwargs)
        self.fields["mentors"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all mentors",
            label="Mentors",
        )
        self.fields["learners"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all learners",
            label="Learners",
        )
        self.fields["content"].widget = widgets.AutocompleteSelectWidget(
            autocomplete_url=f"{reverse_lazy('content-autocomplete')}?{urlencode({'can_be_mentored': True})}",
            placeholder="Select content mentored",
            label="Content",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        def save_m2m():
            instance.learners.add(*self.cleaned_data["learners"])
            for mentor in self.cleaned_data["mentors"]:
                models.MentorPoints.objects.create(
                    account=mentor,
                    submission=instance,
                )

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class EventSubmissionForm(forms.ModelForm):
    class Meta:
        model = models.EventSubmission
        fields = ["name", "hosts", "participants", "donors", "type", "proof", "notes"]

    def __init__(self, *args, **kwargs):
        super(EventSubmissionForm, self).__init__(*args, **kwargs)
        self.fields["hosts"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all hosts",
            label="Hosts",
        )
        self.fields["participants"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all participants",
            label="Participants",
        )
        self.fields["donors"].widget = widgets.AutocompleteSelectMultipleWidget(
            autocomplete_url=f"{reverse_lazy('accounts:account-autocomplete')}?{urlencode({'is_active': True})}",
            placeholder="Select all donors",
            label="Donors",
            required=False,
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        def save_m2m():
            for host in self.cleaned_data["hosts"]:
                models.EventHostPoints.objects.create(
                    account=host,
                    submission=instance,
                )
            for participant in self.cleaned_data["participants"]:
                models.EventParticipantPoints.objects.create(
                    account=participant,
                    submission=instance,
                )
            for donor in self.cleaned_data["donors"]:
                models.EventDonorPoints.objects.create(
                    account=donor,
                    submission=instance,
                )

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance
