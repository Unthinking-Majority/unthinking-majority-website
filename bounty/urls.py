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
        views.BountyListView.as_view(),
        name="index",
    ),
    path(
        "<int:pk>/",
        views.BountyDetail.as_view(),
        name="detail",
    ),
    path(
        "rules/",
        views.CurrentBountyRulesView.as_view(),
        name="rules",
    ),
    path(
        "rules/<int:pk>/",
        views.BountyRulesDetail.as_view(),
        name="rules-detail",
    ),
]
