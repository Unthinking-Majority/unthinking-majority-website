from rest_framework.routers import SimpleRouter

from dragonstone.api import viewsets

router = SimpleRouter()
router.register(
    "dragonstone-base-submissions", viewsets.DragonstoneBaseSubmissionViewSet
)
