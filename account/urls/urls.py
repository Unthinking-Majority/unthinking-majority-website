from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from account import views
from account.urls.autocomplete_urls import autocomplete_urlpatterns

app_name = 'accounts'

urlpatterns = [
    path('profile/',
         login_required(views.ProfileView.as_view()),
         name='profile'),
    path('create-account/',
         views.CreateAccountView.as_view(),
         name='create-account'),

    # Django registration views
    path('login/',
         auth_views.LoginView.as_view(template_name='account/registration/login.html',
                                      redirect_authenticated_user=True),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='account/registration/logged_out.html'),
         name='logout'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='account/registration/password_change_form.html',
             success_url=reverse_lazy('accounts:password_change_done')
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='account/registration/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='account/registration/password_reset_form.html',
             success_url=reverse_lazy('accounts:password_reset_done'),
             email_template_name='account/registration/password_reset_email.html'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='account/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/registration/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
urlpatterns += autocomplete_urlpatterns
