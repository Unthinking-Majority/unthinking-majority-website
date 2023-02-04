from django.urls import path
from django.views.generic import TemplateView

from main import views
from main.urls.autocomplete_urls import autocomplete_urlpatterns

urlpatterns = [
    path('', views.landing, name='landing'),
    path('board/<str:content_category>/<str:content_name>/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('board/pets/', views.PetsLeaderboardView.as_view(), name='pets-leaderboard'),
    path('board/collection-logs/', views.ColLogsLeaderboardView.as_view(), name='col-logs-leaderboard'),
    path('board/combat-achievements/', views.CALeaderboardView.as_view(), name='ca-leaderboard'),
    path('submit-achievement/', views.SubmissionWizard.as_view(), name='submit-achievement'),
    path('form-success/', TemplateView.as_view(template_name='main/forms/success.html'), name='form-success'),
]
urlpatterns += autocomplete_urlpatterns
