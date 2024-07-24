from rest_framework.routers import SimpleRouter

from main.api import viewsets

router = SimpleRouter()
router.register("content-categories", viewsets.ContentCateogryViewSet)
router.register("contents", viewsets.ContentViewSet)
router.register("boards", viewsets.BoardViewSet)
router.register("settings", viewsets.SettingsViewSet)
