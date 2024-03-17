from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from main.api.urls import router as main_router

router = DefaultRouter()
router.registry.extend(main_router.registry)

admin.site.site_header = "UM Administration"

urlpatterns = [
    path("", include("main.urls")),
    path("api/", include(router.urls)),
    path("achievements/", include("achievements.urls", namespace="achievements")),
    path("dragonstone/", include("dragonstone.urls", namespace="dragonstone")),
    path("bounty/", include("bounty.urls", namespace="bounty")),
    path("admin/", admin.site.urls),
    path("accounts/", include("account.urls", namespace="account")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
    path(
        "inbox/notifications/", include("notifications.urls", namespace="notifications")
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    from django.views.generic import TemplateView

    urlpatterns.insert(0, path("__reload__/", include("django_browser_reload.urls")))
    urlpatterns += [
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", TemplateView.as_view(template_name="500.html")),
    ]
