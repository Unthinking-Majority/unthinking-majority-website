from django.urls import path

from dragonstone import views

app_name = "dragonstone"

urlpatterns = [
    path(
        "submit/",
        views.DragonstoneSubmissionWizard.as_view(),
        name="submit-dragonstone",
    ),
]
