import os

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView

from achievements import CA, COL_LOG, PET, RECORD, forms


def pet_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("submission_type_form") or {}
    return cleaned_data.get("type", None) == PET


def col_logs_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("submission_type_form") or {}
    return cleaned_data.get("type", None) == COL_LOG


def ca_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("submission_type_form") or {}
    return cleaned_data.get("type", None) == CA


def select_content_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("submission_type_form") or {}
    return cleaned_data.get("type", None) == RECORD


def select_board_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("select_content_form") or {}
    content = cleaned_data.get("content")
    return content and content.boards.count() > 1


def board_submission_form_condition(wizard):
    return wizard.get_cleaned_data_for_step("select_content_form") or None


class SubmissionWizard(SessionWizardView):
    """
    Main form wizard for dictating the submission process.
    Helps the user navigate the decision tree to the correct form for their submission.
    """

    form_list = [
        ("submission_type_form", forms.SelectSubmissionTypeForm),
        ("select_content_form", forms.SelectContentForm),
        ("select_board_form", forms.SelectBoardForm),
        ("record_submission_form", forms.RecordSubmissionForm),
        ("pet_submission_form", forms.PetSubmissionForm),
        ("col_logs_submission_form", forms.ColLogSubmissionForm),
        ("ca_submission_form", forms.CASubmissionForm),
    ]
    TEMPLATES = {
        "submission_type_form": "achievements/forms/wizard/select_submission_type_form.html",
        "select_content_form": "achievements/forms/wizard/select_content_form.html",
        "select_board_form": "achievements/forms/wizard/select_board_form.html",
        "record_submission_form": "achievements/forms/wizard/record_submission_form.html",
        "pet_submission_form": "achievements/forms/wizard/pet_submission_form.html",
        "col_logs_submission_form": "achievements/forms/wizard/col_logs_submission_form.html",
        "ca_submission_form": "achievements/forms/wizard/ca_submission_form.html",
    }
    condition_dict = {
        "select_content_form": select_content_form_condition,
        "select_board_form": select_board_form_condition,
        "record_submission_form": board_submission_form_condition,
        "pet_submission_form": pet_submission_form_condition,
        "col_logs_submission_form": col_logs_submission_form_condition,
        "ca_submission_form": ca_submission_form_condition,
    }
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, "temp_files")
    )

    def post(self, *args, **kwargs):
        wizard_goto_step = self.request.POST.get("wizard_goto_step", None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            self.storage.set_step_data(self.steps.current, None)
        return super(SubmissionWizard, self).post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get("form_dict")
        if "record_submission_form" in form_dict.keys():
            form_dict["record_submission_form"].save()
        elif "pet_submission_form" in form_dict.keys():
            form_dict["pet_submission_form"].form_valid()
        elif "col_logs_submission_form" in form_dict.keys():
            form_dict["col_logs_submission_form"].save()
        elif "ca_submission_form" in form_dict.keys():
            form_dict["ca_submission_form"].save()

        messages.success(self.request, "Your form has been successfully submitted.")
        return redirect("/")

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == "select_board_form":
            context.update(
                {
                    "content": self.get_cleaned_data_for_step("select_content_form")[
                        "content"
                    ]
                }
            )
        if self.steps.current == "record_submission_form":
            if self.get_cleaned_data_for_step("select_board_form"):
                board = self.get_cleaned_data_for_step("select_board_form").get("board")
            else:
                board = (
                    self.get_cleaned_data_for_step("select_content_form")
                    .get("content")
                    .boards.first()
                )
            context.update({"board": board})
        return context

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == "select_board_form":
            cleaned_data = self.get_cleaned_data_for_step("select_content_form")
            kwargs.update({"content": cleaned_data.get("content")})
        if step == "record_submission_form":
            if self.get_cleaned_data_for_step("select_board_form"):
                board = self.get_cleaned_data_for_step("select_board_form").get("board")
            else:
                board = (
                    self.get_cleaned_data_for_step("select_content_form")
                    .get("content")
                    .boards.first()
                )
            kwargs.update({"board": board})
        return kwargs

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if hasattr(self.request.user, "account"):
            initial.update({"account": getattr(self.request.user, "account", None)})
        return initial

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
