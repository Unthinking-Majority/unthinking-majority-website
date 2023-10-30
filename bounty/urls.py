from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from bounty import views

app_name = "bounty"

urlpatterns = [
    path(
        "",
        staff_member_required(views.CurrentBountyView.as_view()),
        name="current-bounty",
    ),
    path(
        "index/",
        staff_member_required(views.BountyIndexView.as_view()),
        name="bounty-index",
    ),
    path(
        "<int:id>/",
        staff_member_required(views.BountyView.as_view()),
        name="bounty-view",
    ),
    path(
        "rules/",
        staff_member_required(views.BountyRulesView.as_view()),
        name="bounty-rules",
    ),
]
