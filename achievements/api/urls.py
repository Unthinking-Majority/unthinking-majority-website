from rest_framework.routers import SimpleRouter

from achievements.api import viewsets

router = SimpleRouter()
router.register("base_submissions", viewsets.BaseSubmissionViewSet)
router.register("record_submissions", viewsets.RecordSubmissionViewSet)
