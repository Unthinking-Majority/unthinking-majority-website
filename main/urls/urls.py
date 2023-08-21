from django.urls import path
from django.views.generic import TemplateView

from main import views
from main.urls.autocomplete_urls import autocomplete_urlpatterns

urlpatterns = [
    path("", views.landing, name="landing"),
    path(
        "board/<str:content_category>/<str:content_name>/",
        views.LeaderboardView.as_view(),
        name="leaderboard",
    ),
    path("board/pets/", views.PetsLeaderboardView.as_view(), name="pets-leaderboard"),
    path(
        "board/collection-logs/",
        views.ColLogsLeaderboardView.as_view(),
        name="col-logs-leaderboard",
    ),
    path(
        "board/combat-achievements/",
        views.CALeaderboardView.as_view(),
        name="ca-leaderboard",
    ),
    path(
        "form-success/",
        TemplateView.as_view(template_name="main/forms/success.html"),
        name="form-success",
    ),
    path(
        "mark-notification-as-read/<int:notification_id>/",
        views.MarkNotificationAsRead.as_view(),
        name="mark-notification-as-read",
    ),
]
urlpatterns += autocomplete_urlpatterns
