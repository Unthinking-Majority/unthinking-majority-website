from django.contrib.admin.views.decorators import staff_member_required as smr
from django.urls import path

from dragonstone import views

urlpatterns = [
    path('submit/dragonstone/', smr(views.DragonstoneSubmissionWizard.as_view()), name='submit-dragonstone'),
]
