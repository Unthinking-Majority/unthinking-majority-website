from rest_framework.routers import SimpleRouter

from account.api import viewsets

router = SimpleRouter()
router.register("accounts", viewsets.AccountViewSet)
