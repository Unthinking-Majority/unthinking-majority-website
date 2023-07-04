from django.urls import path

from bounty import views

app_name = "bounty"

urlpatterns = [
    path("", views.CurrentBountyView.as_view(), name="current-bounty"),
    path("index/", views.BountyIndex.as_view(), name="bounty-index"),
    path("<int:id>/", views.BountyView.as_view(), name="bounty-view"),
]
