from rest_framework.routers import SimpleRouter

from main.api import viewsets

router = SimpleRouter()
router.register("content_categories", viewsets.ContentCateogryViewSet)
router.register("contents", viewsets.ContentViewSet)
router.register("boards", viewsets.BoardViewSet)
router.register("constance", viewsets.ConstanceViewSet)
