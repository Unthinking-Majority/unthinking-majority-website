from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from account.models import Account
from main import forms
from main.models import Board, Submission


def landing(request):
    return render(
        request,
        'landing.html',
    )


class BoardView(ListView):
    model = Submission
    template_name = 'board.html'
    paginate_by = 5

    def get_queryset(self):
        return self.model.objects.filter(
            board__slug=self.kwargs.get('board_name'),
            accepted=True
        ).order_by('value')
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BoardView, self).get_context_data()
        context['board'] = get_object_or_404(
           Board.objects.prefetch_related('submissions'),
            slug=self.kwargs.get('board_name')
        )
        return context


class SubmissionView(CreateView):
    model = Submission
    form_class = forms.SubmissionForm
    template_name = 'forms/submission_create_form.html'

    def get_form_kwargs(self):
        kwargs = super(SubmissionView, self).get_form_kwargs()

        if self.request.user.is_authenticated and self.request.method == 'POST':
            data = self.request.POST.copy()
            data.update({'account': self.request.user.account.id})
            kwargs.update({'data': data})

        return kwargs

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'Form submission successful. Your submission is now under review.')
        return self.render_to_response(self.get_context_data(form=form))
