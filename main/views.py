import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Subquery, Count, F, Q
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from formtools.wizard.views import SessionWizardView

from main import RECORD, PET, COL_LOG, CA
from main import forms
from main import models


def landing(request):
    return render(
        request,
        'main/landing.html',
    )


class LeaderboardView(TemplateView):
    template_name = 'main/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_board'] = get_object_or_404(
            models.ParentBoard.objects.prefetch_related('boards__submissions'),
            slug=self.kwargs.get('parent_board_name')
        )

        context['data'] = []
        for board in context['parent_board'].boards.all():

            # filter out submissions whose inactive accounts account for at least half of the accounts
            active_accounts_submissions = board.submissions.accepted().annotate(
                num_accounts=Count('accounts'),
                num_active_accounts=Count('accounts', filter=Q(accounts__active=True))
            ).filter(num_active_accounts__gt=F('num_accounts') / 2)

            # group by accounts and value, then select distinct; this way, we only get 1 entry from each user!
            submissions_subquery = models.Submission.objects.filter(
                pk__in=Subquery(active_accounts_submissions.values('pk'))
            ).order_by().order_by(
                'accounts',
                'value'
            ).distinct(
                'accounts'
            )

            submissions = models.Submission.objects.filter(
                pk__in=Subquery(submissions_subquery.values('pk'))
            ).order_by('value')

            p = Paginator(submissions, 5)
            page = p.page(self.request.GET.get(f'{board.id}__page', 1))
            context['data'].append((board, page))

        return context


def pet_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == PET


def col_logs_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == COL_LOG


def ca_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == CA


def select_parent_board_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == RECORD


def select_board_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('select_parent_board_form') or {}
    parent_board = cleaned_data.get('parent_board')
    return parent_board and parent_board.boards.count() > 1


def board_submission_form_condition(wizard):
    return wizard.get_cleaned_data_for_step('select_parent_board_form') or None


class SubmissionWizard(SessionWizardView):
    form_list = [
        ('submission_type_form', forms.SelectSubmissionTypeForm),
        ('select_parent_board_form', forms.SelectParentBoardForm),
        ('select_board_form', forms.SelectBoardForm),
        ('board_submission_form', forms.BoardSubmissionForm),
        ('pet_submission_form', forms.PetSubmissionForm),
        ('col_logs_submission_form', forms.ColLogSubmissionForm),
        ('ca_submission_form', forms.CASubmissionForm),
    ]
    TEMPLATES = {
        'submission_type_form': 'main/forms/wizard/select_submission_type_form.html',
        'select_parent_board_form': 'main/forms/wizard/select_parent_board_form.html',
        'select_board_form': 'main/forms/wizard/select_board_form.html',
        'board_submission_form': 'main/forms/wizard/board_submission_form.html',
        'pet_submission_form': 'main/forms/wizard/pet_submission_form.html',
        'col_logs_submission_form': 'main/forms/wizard/col_logs_submission_form.html',
        'ca_submission_form': 'main/forms/wizard/ca_submission_form.html',
    }
    condition_dict = {
        'select_parent_board_form': select_parent_board_form_condition,
        'select_board_form': select_board_form_condition,
        'board_submission_form': board_submission_form_condition,
        'pet_submission_form': pet_submission_form_condition,
        'col_logs_submission_form': col_logs_submission_form_condition,
        'ca_submission_form': ca_submission_form_condition,
    }
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_files'))

    def post(self, *args, **kwargs):
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            self.storage.set_step_data(self.steps.current, None)
        return super(SubmissionWizard, self).post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get('form_dict')
        if 'board_submission_form' in form_dict.keys():
            submission = models.Submission.objects.create(
                value=form_dict['board_submission_form'].cleaned_data['value'],
                proof=form_dict['board_submission_form'].cleaned_data['proof'],
                notes=form_dict['board_submission_form'].cleaned_data['notes'],
                board=form_dict['board_submission_form'].cleaned_data['board']
            )
            submission.accounts.set(form_dict['board_submission_form'].cleaned_data['accounts'])
        elif 'pet_submission_form' in form_dict.keys():
            first_submission = models.Submission.objects.create(
                type=PET,
                pet=form_dict['pet_submission_form'].cleaned_data['pets'][0],
                notes=form_dict['pet_submission_form'].cleaned_data['notes'],
                proof=form_dict['pet_submission_form'].cleaned_data['proof'],
            )
            first_submission.accounts.add(form_dict['pet_submission_form'].cleaned_data['account'])
            for pet in form_dict['pet_submission_form'].cleaned_data['pets'][1:]:
                submission = models.Submission.objects.create(
                    type=PET,
                    pet=pet,
                    notes=form_dict['pet_submission_form'].cleaned_data['notes'],
                    proof=first_submission.proof,  # re-use the already uploaded file!
                )
                submission.accounts.add(form_dict['pet_submission_form'].cleaned_data['account'])
        elif 'col_logs_submission_form' in form_dict.keys():
            submission = models.Submission.objects.create(
                type=COL_LOG,
                value=form_dict['col_logs_submission_form'].cleaned_data['col_logs'],
                notes=form_dict['col_logs_submission_form'].cleaned_data['notes'],
                proof=form_dict['col_logs_submission_form'].cleaned_data['proof'],
            )
            submission.accounts.add(form_dict['col_logs_submission_form'].cleaned_data['account'])
        elif 'ca_submission_form' in form_dict.keys():
            submission = models.Submission.objects.create(
                type=CA,
                combat_achievement_tier=form_dict['ca_submission_form'].cleaned_data['combat_achievement_tier'],
                notes=form_dict['ca_submission_form'].cleaned_data['notes'],
                proof=form_dict['ca_submission_form'].cleaned_data['proof'],
            )
            submission.accounts.add(form_dict['ca_submission_form'].cleaned_data['account'])

        return redirect(reverse('form-success'))

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'select_board_form':
            context.update({'parent_board': self.get_cleaned_data_for_step('select_parent_board_form')['parent_board']})
        if self.steps.current == 'board_submission_form':
            if self.get_cleaned_data_for_step('select_board_form'):
                board = self.get_cleaned_data_for_step('select_board_form').get('board')
            else:
                board = self.get_cleaned_data_for_step('select_parent_board_form').get('parent_board').boards.first()
            context.update({'board': board})
        return context

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'select_board_form':
            cleaned_data = self.get_cleaned_data_for_step('select_parent_board_form')
            kwargs.update({'parent_board': cleaned_data['parent_board']})
        if step == 'board_submission_form':
            if self.get_cleaned_data_for_step('select_board_form'):
                board = self.get_cleaned_data_for_step('select_board_form').get('board')
            else:
                board = self.get_cleaned_data_for_step('select_parent_board_form').get('parent_board').boards.first()
            kwargs.update({'board': board})
        return kwargs

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
