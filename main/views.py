from collections import Counter

from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import render

from main.models import BoardCategory, Submission


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
            'board_categories': BoardCategory.objects.all(),
            'recent_submissions': Submission.objects.order_by('date')[:5],
            'first_places': first_places,
        }
    )
