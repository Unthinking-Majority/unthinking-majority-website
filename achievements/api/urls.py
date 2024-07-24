from rest_framework.routers import SimpleRouter

from achievements.api import viewsets

router = SimpleRouter()
router.register("base-submissions", viewsets.BaseSubmissionViewSet)
router.register("record-submissions", viewsets.RecordSubmissionViewSet)
