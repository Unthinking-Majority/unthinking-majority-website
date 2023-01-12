from django.urls import path
from django.views.generic import TemplateView

from main import views
from main.urls.autocomplete_urls import autocomplete_urlpatterns

urlpatterns = [
    path('', views.landing, name='landing'),
    path('board/<str:board_category>/<str:parent_board_name>/', views.LeaderBoardsListView.as_view(), name='board'),
    path('submit-achievement/', views.SubmissionWizard.as_view(), name='submit-achievement'),
    path('form-success/', TemplateView.as_view(template_name='main/forms/success.html'), name='form-success'),
]
urlpatterns += autocomplete_urlpatterns
