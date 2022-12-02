from collections import Counter

from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView

from main.models import Board, Submission


def landing(request):
    temp = Submission.objects.values('board').annotate(Max('value')).values_list('user', flat=True)
    first_places = [
        {'user': User.objects.get(pk=pk), 'val': val}
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
