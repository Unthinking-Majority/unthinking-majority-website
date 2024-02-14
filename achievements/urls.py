from constance import config
from django.urls import path
from django.views.generic.base import TemplateView

from achievements import views
from main.models import Board

app_name = "achievements"

urlpatterns = [
    path(
        "submit/",
        views.SubmissionWizard.as_view(),
        name="submit-achievement",
    ),
    path(
        "point-multipliers/",
        TemplateView.as_view(
            template_name="achievements/point_breakdown.html",
            extra_context={
                "boards": Board.objects.filter(
                    content__has_pbs=True, is_active=True
                ).order_by("content__name", "name"),
                "config": config,
            },
        ),
    ),
]
