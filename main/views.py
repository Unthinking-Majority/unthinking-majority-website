from collections import Counter

from django.contrib import messages
from django.db.models import Max
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from account.models import Account
from main import forms
from main.models import Board, Submission


def landing(request):
    temp = Submission.objects.accepted().values('board').annotate(Max('value')).values_list('account', flat=True)
    first_places = [
        {'account': Account.objects.get(pk=pk), 'val': val}
        for pk, val in Counter(temp).most_common(5)
    ]

    return render(
        request,
        'landing.html',
        {
            'recent_submissions': Submission.objects.accepted().order_by('date')[:5],
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


class SubmissionView(CreateView):
    model = Submission
    form_class = forms.SubmissionForm
    template_name = 'forms/submission_create_form.html'

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.account = Account.objects.get(user=self.request.user)
        submission.save()

        messages.success(self.request, 'Form submission successful. Your submission is now under review.')

        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        else:
            return super(SubmissionView, self).dispatch(request, *args, **kwargs)
