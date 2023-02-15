import os

from django.conf import settings
from django.contrib.postgres.aggregates import StringAgg
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count, F, Q, OuterRef
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView

from account.models import Account
from achievements import RECORD, PET, COL_LOG, CA
from main import forms
from achievements import models as achievements_models
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
        context['content'] = get_object_or_404(
            models.Content.objects.prefetch_related('boards__submissions'),
            slug=self.kwargs.get('content_name')
        )

        context['data'] = []
        ordering = context['content'].ordering
        num_objs_per_page = 10 if context['content'].boards.count() == 1 else 5
        for board in context['content'].boards.all():

            # filter out submissions whose inactive accounts account for at least half of the accounts
            active_accounts_submissions = board.submissions.accepted().annotate(
                num_accounts=Count('accounts'),
                num_active_accounts=Count('accounts', filter=Q(accounts__active=True))
            ).filter(num_active_accounts__gt=F('num_accounts') / 2)

            # annotate the teams (accounts values) into a string so we can order by unique teams of accounts and value
            annotated_submissions = active_accounts_submissions.annotate(
                accounts_str=StringAgg('accounts__name', delimiter=',', ordering='accounts__name')
            ).order_by('accounts_str', f'{ordering}value')

            # grab the first submission for each team (which is the best, since we ordered by value above)
            submissions = {}
            for submission in annotated_submissions:
                if submission.accounts_str not in submissions.keys():
                    submissions[submission.accounts_str] = submission.id
            submissions = achievements_models.RecordSubmission.objects.filter(
                id__in=submissions.values()
            ).order_by(f'{ordering}value', 'date')

            p = Paginator(submissions, num_objs_per_page)
            try:
                page = p.page(self.request.GET.get(f'{board.id}__page', 1))
            except EmptyPage:
                page = p.page(1)
            context['data'].append((board, page))

        return context


class PetsLeaderboardView(ListView):
    model = Account
    template_name = 'main/leaderboards/pets_leaderboard.html'
    paginate_by = 10

    def get_queryset(self):
        # get accepted pet submissions
        pet_submissions = achievements_models.PetSubmission.objects.accepted()

        # create sub query, to annotate the number of pets per account
        sub_query = pet_submissions.values('account').annotate(num_pets=Count('account')).filter(account__id=OuterRef('id'))

        # annotate num_pets per account using sub query ; filter out null values ; order by number of pets descending
        accounts = Account.objects.annotate(num_pets=sub_query.values('num_pets')[:1]).filter(
            num_pets__isnull=False,
            active=True
        ).order_by('-num_pets')

        return accounts


class ColLogsLeaderboardView(ListView):
    model = Account
    template_name = 'main/leaderboards/col_logs_leaderboard.html'
    paginate_by = 10

    def get_queryset(self):
        # get accepted collection log submissions ; use empty order_by() to clear any ordering
        col_logs_submissions = achievements_models.ColLogSubmission.objects.accepted().order_by().filter(account__active=True)

        # create sub query, which grabs the Max col_log value for each account
        sub_query = col_logs_submissions.order_by('account', '-col_logs').distinct('account')

        # filter for submissions which have a matching id from the above sub query ; order by value descending
        submissions = achievements_models.ColLogSubmission.objects.filter(id__in=sub_query.values('id')).order_by('-col_logs', 'date')

        return submissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['max_col_log'] = settings.MAX_COL_LOG
        return context


class CALeaderboardView(ListView):
    model = Account
    template_name = 'main/leaderboards/ca_leaderboard.html'
    paginate_by = 10

    def get_queryset(self):
        # get accepted combat achievement submissions ; use empty order_by() to clear any ordering
        ca_submissions = achievements_models.CASubmission.objects.accepted().order_by().filter(account__active=True)

        # create sub query, which grabs the best ca tier value for each account
        sub_query = ca_submissions.order_by('account', 'ca_tier').distinct('account')

        # filter for submissions which have a matching id from the above sub query ; order by ca_tier descending
        submissions = achievements_models.CASubmission.objects.filter(id__in=sub_query.values('id')).order_by('ca_tier', 'date')
        return submissions


def pet_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == PET


def col_logs_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == COL_LOG


def ca_submission_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == CA


def select_content_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('submission_type_form') or {}
    return cleaned_data.get('type', None) == RECORD


def select_board_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('select_content_form') or {}
    content = cleaned_data.get('content')
    return content and content.boards.count() > 1


def board_submission_form_condition(wizard):
    return wizard.get_cleaned_data_for_step('select_content_form') or None


class SubmissionWizard(SessionWizardView):
    """
    Main form wizard for dictating the submission process.
    Helps the user navigate the decision tree to the correct form for their submission.
    """
    form_list = [
        ('submission_type_form', forms.SelectSubmissionTypeForm),
        ('select_content_form', forms.SelectContentForm),
        ('select_board_form', forms.SelectBoardForm),
        ('record_submission_form', forms.RecordSubmissionForm),
        ('pet_submission_form', forms.PetSubmissionForm),
        ('col_logs_submission_form', forms.ColLogSubmissionForm),
        ('ca_submission_form', forms.CASubmissionForm),
    ]
    TEMPLATES = {
        'submission_type_form': 'main/forms/wizard/select_submission_type_form.html',
        'select_content_form': 'main/forms/wizard/select_content_form.html',
        'select_board_form': 'main/forms/wizard/select_board_form.html',
        'record_submission_form': 'main/forms/wizard/record_submission_form.html',
        'pet_submission_form': 'main/forms/wizard/pet_submission_form.html',
        'col_logs_submission_form': 'main/forms/wizard/col_logs_submission_form.html',
        'ca_submission_form': 'main/forms/wizard/ca_submission_form.html',
    }
    condition_dict = {
        'select_content_form': select_content_form_condition,
        'select_board_form': select_board_form_condition,
        'record_submission_form': board_submission_form_condition,
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
        if 'record_submission_form' in form_dict.keys():
            form_dict['record_submission_form'].save()
        elif 'pet_submission_form' in form_dict.keys():
            form_dict['pet_submission_form'].form_valid()
        elif 'col_logs_submission_form' in form_dict.keys():
            form_dict['col_logs_submission_form'].save()
        elif 'ca_submission_form' in form_dict.keys():
            form_dict['ca_submission_form'].save()

        return redirect(reverse('form-success'))

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'select_board_form':
            context.update({'content': self.get_cleaned_data_for_step('select_content_form')['content']})
        if self.steps.current == 'record_submission_form':
            if self.get_cleaned_data_for_step('select_board_form'):
                board = self.get_cleaned_data_for_step('select_board_form').get('board')
            else:
                board = self.get_cleaned_data_for_step('select_content_form').get('content').boards.first()
            context.update({'board': board})
        return context

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'select_board_form':
            cleaned_data = self.get_cleaned_data_for_step('select_content_form')
            kwargs.update({'content': cleaned_data.get('content')})
        if step == 'record_submission_form':
            if self.get_cleaned_data_for_step('select_board_form'):
                board = self.get_cleaned_data_for_step('select_board_form').get('board')
            else:
                board = self.get_cleaned_data_for_step('select_content_form').get('content').boards.first()
            kwargs.update({'board': board})
        return kwargs

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
