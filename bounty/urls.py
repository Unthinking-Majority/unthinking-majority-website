from django.urls import path

from bounty import views

app_name = "bounty"

urlpatterns = [
    path(
        "",
        views.CurrentBountyView.as_view(),
        name="current-bounty",
    ),
    path(
        "index/",
        views.BountyIndexView.as_view(),
        name="bounty-index",
    ),
    path(
        "<int:pk>/",
        views.BountyView.as_view(),
        name="detail",
    ),
    path(
        "rules/",
        views.CurrentBountyRulesView.as_view(),
        name="rules",
    ),
    path(
        "rules/<int:pk>/",
        views.BountyRulesDetailView.as_view(),
        name="rules-detail",
    ),
]
