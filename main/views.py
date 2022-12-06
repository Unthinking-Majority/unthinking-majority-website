from collections import Counter

from django.db.models import Max
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from account.models import Account
from main import forms
from main.models import Board, Submission


def landing(request):
    temp = Submission.objects.values('board').annotate(Max('value')).values_list('account', flat=True)
    first_places = [
        {'account': Account.objects.get(pk=pk), 'val': val}
        for pk, val in Counter(temp).most_common(5)
    ]

    return render(
        request,
        'landing.html',
        {
            'recent_submissions': Submission.objects.order_by('date')[:5],
            'first_places': first_places,
        }
    )


class BoardView(TemplateView):
    template_name = 'board.html'

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context['board'] = get_object_or_404(
            Board.objects.prefetch_related('submissions'),
            slug=kwargs.get('board_name')
        )
        return context


class SubmissionView(FormView):
    template_name = 'submission_form.html'
    form_class = forms.SubmissionForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        form.save()
        return super(SubmissionView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        else:
            return super(SubmissionView, self).dispatch(request, *args, **kwargs)
