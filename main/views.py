import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView

from main import RECORD, PET, COL_LOG
from main import forms
from main import models


def landing(request):
    return render(
        request,
        'main/landing.html',
    )


class BoardSubmissionsListView(ListView):
    model = models.Submission
    template_name = 'main/board.html'
    paginate_by = 5

    def get_queryset(self):
        return self.model.objects.records().filter(
            board__slug=self.kwargs.get('board_name'),
            accepted=True
        ).order_by('value')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BoardSubmissionsListView, self).get_context_data()
        context['board'] = get_object_or_404(
            models.Board.objects.prefetch_related('submissions'),
            slug=self.kwargs.get('board_name')
        )
        return context


def pet_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == PET


def col_logs_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == COL_LOG


def select_board_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == RECORD


def record_form_condition(wizard):
    return wizard.get_cleaned_data_for_step('select_board_form') or None


class SubmissionWizard(SessionWizardView):
    form_list = [
        ('submission_type_form', forms.SelectSubmissionTypeForm),
        ('pet_form', forms.PetForm),
        ('col_logs_form', forms.CollectionLogForm),
        ('select_board_form', forms.SelectBoardForm),
        ('record_form', forms.BoardSubmissionForm),
    ]
    TEMPLATES = {
        'submission_type_form': 'main/forms/wizard/select_submission_type_form.html',
        'pet_form': 'main/forms/wizard/pet_form.html',
        'col_logs_form': 'main/forms/wizard/col_logs_form.html',
        'select_board_form': 'main/forms/wizard/select_board_form.html',
        'record_form': 'main/forms/wizard/record_form.html',
    }
    condition_dict = {
        'pet_form': pet_form_condition,
        'col_logs_form': col_logs_form_condition,
        'select_board_form': select_board_form_condition,
        'record_form': record_form_condition,
    }
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_files'))

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get('form_dict')
        if 'record_form' in form_dict.keys():
            accounts = [val for key, val in form_dict['record_form'].cleaned_data.items() if 'account' in key]
            submission = models.Submission.objects.create(
                value=form_dict['record_form'].cleaned_data['value'],
                proof=form_dict['record_form'].cleaned_data['proof'],
                notes=form_dict['record_form'].cleaned_data['notes'],
                board=form_dict['select_board_form'].cleaned_data['board']
            )
            submission.accounts.set(accounts)
        elif 'pet_form' in form_dict.keys():
            submission = models.Submission.objects.create(
                type=PET,
                pet=form_dict['pet_form'].cleaned_data['pet'],
                notes=form_dict['pet_form'].cleaned_data['notes'],
                proof=form_dict['pet_form'].cleaned_data['proof'],
            )
            submission.accounts.add(form_dict['pet_form'].cleaned_data['account'])
        elif 'col_logs_form' in form_dict.keys():
            submission = models.Submission.objects.create(
                type=COL_LOG,
                value=form_dict['col_logs_form'].cleaned_data['col_logs'],
                notes=form_dict['col_logs_form'].cleaned_data['notes'],
                proof=form_dict['col_logs_form'].cleaned_data['proof'],
            )
            submission.accounts.add(form_dict['col_logs_form'].cleaned_data['account'])
        else:
            # error
            pass
        return redirect(reverse('form-success'))

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'record_form':
            cleaned_data = self.get_cleaned_data_for_step('select_board_form')
            kwargs.update({'team_size': cleaned_data['team_size']})
        return kwargs

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
