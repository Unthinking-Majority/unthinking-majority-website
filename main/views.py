from django.shortcuts import render

from main.models import Board, Submission


def landing(request):
    return render(
        request,
        'landing.html',
        {
            'boards': Board.objects.all(),
            'recent_submissions': Submission.objects.order_by('date')[:5],
        }
    )
