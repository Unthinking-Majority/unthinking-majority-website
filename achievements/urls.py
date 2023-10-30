from django.urls import path

from achievements import views

app_name = "achievements"

urlpatterns = [
    path(
        "submit/achievement/",
        views.SubmissionWizard.as_view(),
        name="submit-achievement",
    ),
]
