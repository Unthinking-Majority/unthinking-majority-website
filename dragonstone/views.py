import os

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView

from dragonstone import EVENT, MENTOR, PVM_SPLIT, forms


def pvm_split_form_condition(wizard):
    cleaned_data = (
        wizard.get_cleaned_data_for_step("dragonstone_submission_type_form") or {}
    )
    return cleaned_data.get("type", None) == PVM_SPLIT


def mentor_form_condition(wizard):
    cleaned_data = (
        wizard.get_cleaned_data_for_step("dragonstone_submission_type_form") or {}
    )
    return cleaned_data.get("type", None) == MENTOR


def event_form_condition(wizard):
    cleaned_data = (
        wizard.get_cleaned_data_for_step("dragonstone_submission_type_form") or {}
    )
    return cleaned_data.get("type", None) == EVENT


class DragonstoneSubmissionWizard(SessionWizardView):
    """
    Main form wizard for dictating the submission process.
    Helps the user navigate the decision tree to the correct form for their submission.
    """

    form_list = [
        ("dragonstone_submission_type_form", forms.SelectDragonstoneSubmissionTypeForm),
        ("pvm_split_submission_form", forms.PVMSplitSubmissionForm),
        ("mentor_submission_form", forms.MentorSubmissionForm),
        ("event_submission_form", forms.EventSubmissionForm),
    ]
    TEMPLATES = {
        "dragonstone_submission_type_form": "dragonstone/forms/wizard/dragonstone_submission_type_form.html",
        "pvm_split_submission_form": "dragonstone/forms/wizard/pvm_split_submission_form.html",
        "mentor_submission_form": "dragonstone/forms/wizard/mentor_submission_form.html",
        "event_submission_form": "dragonstone/forms/wizard/event_submission_form.html",
    }
    condition_dict = {
        "pvm_split_submission_form": pvm_split_form_condition,
        "mentor_submission_form": mentor_form_condition,
        "event_submission_form": event_form_condition,
    }
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, "temp_files")
    )

    def post(self, *args, **kwargs):
        wizard_goto_step = self.request.POST.get("wizard_goto_step", None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            self.storage.set_step_data(self.steps.current, None)
        return super(DragonstoneSubmissionWizard, self).post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get("form_dict")

        if "pvm_split_submission_form" in form_dict.keys():
            form_dict["pvm_split_submission_form"].save()
        elif "mentor_submission_form" in form_dict.keys():
            form_dict["mentor_submission_form"].save()
        elif "event_submission_form" in form_dict.keys():
            form_dict["event_submission_form"].save()

        messages.success(self.request, "Form successfully submitted.")
        return redirect("/")

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
