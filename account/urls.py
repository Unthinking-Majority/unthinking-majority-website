from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path

from account import views

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='account/registration/login.html', redirect_authenticated_user=True),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='account/registration/logged_out.html'),
        name='logout'
    ),
    path(
        'profile/',
        login_required(views.ProfileView.as_view()),
        name='profile',
    ),
]
