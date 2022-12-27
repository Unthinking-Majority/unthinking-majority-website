from django.urls import path

from main import views
from main.urls.autocomplete_urls import autocomplete_urlpatterns

urlpatterns = [
    path('', views.landing, name='landing'),
    path('board/<str:board_category>/<str:board_name>/', views.BoardView.as_view(), name='board'),
    path('submit-achievement/', views.SubmissionWizard.as_view(), name='submit-achievement'),
]
urlpatterns += autocomplete_urlpatterns
