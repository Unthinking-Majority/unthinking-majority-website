from django.urls import path

from bounty import views

urlpatterns = [
    path("bounty/", views.BountyView.as_view(), name="bounty"),
]
