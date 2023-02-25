from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'UM Administration'

urlpatterns = [
    path('', include('main.urls')),
    path('', include('achievements.urls')),
    path('', include('dragonstone.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls', namespace='account')),
    path('__reload__/', include('django_browser_reload.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    from django.views.generic import TemplateView
    urlpatterns += [
        path('404/', TemplateView.as_view(template_name='404.html')),
        path('500/', TemplateView.as_view(template_name='500.html')),
    ]
