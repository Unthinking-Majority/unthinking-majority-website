from django.conf import settings
from django.contrib.postgres.aggregates import StringAgg
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count, OuterRef
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from account.models import Account
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

            active_accounts_submissions = board.submissions.active_submissions().accepted()

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
            is_active=True
        ).order_by('-num_pets')

        return accounts


class ColLogsLeaderboardView(ListView):
    model = Account
    template_name = 'main/leaderboards/col_logs_leaderboard.html'
    paginate_by = 10

    def get_queryset(self):
        # get accepted collection log submissions ; use empty order_by() to clear any ordering
        col_logs_submissions = achievements_models.ColLogSubmission.objects.accepted().order_by().filter(account__is_active=True)

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
        ca_submissions = achievements_models.CASubmission.objects.accepted().order_by().filter(account__is_active=True)

        # create sub query, which grabs the best ca tier value for each account
        sub_query = ca_submissions.order_by('account', 'ca_tier').distinct('account')

        # filter for submissions which have a matching id from the above sub query ; order by ca_tier descending
        submissions = achievements_models.CASubmission.objects.filter(id__in=sub_query.values('id')).order_by('ca_tier', 'date')
        return submissions
