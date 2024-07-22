from django.urls import path
from django.views.generic.base import TemplateView

from dragonstone import views
from main.config import config

app_name = "dragonstone"

urlpatterns = [
    path(
        "submit/",
        views.DragonstoneSubmissionWizard.as_view(),
        name="submit-dragonstone",
    ),
    path(
        "points-breakdown/",
        TemplateView.as_view(
            template_name="dragonstone/points_breakdown.html",
            extra_context={
                "config": config,
            },
        ),
        name="points-breakdown",
    ),
]
