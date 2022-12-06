from django.urls import path

from main import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('board/<str:board_category>/<str:board_name>/', views.BoardView.as_view(), name='board'),
    path('submit-pb/', views.SubmissionView.as_view(), name='submit-pb'),
]
