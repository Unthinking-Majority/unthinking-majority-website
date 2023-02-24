from django.urls import path

from dragonstone import views

urlpatterns = [
    path('submit/dragonstone/', views.DragonstoneSubmissionWizard.as_view(), name='submit-dragonstone'),
]
