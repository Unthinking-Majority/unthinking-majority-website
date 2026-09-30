from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from achievements.api.serializers import RecordSubmissionSerializer
from main import models
from main.api import serializers


class ContentCateogryViewSet(viewsets.ModelViewSet):
    queryset = models.ContentCategory.objects.all()
    serializer_class = serializers.ContentCategorySerializer


class ContentViewSet(viewsets.ModelViewSet):
    queryset = models.Content.objects.select_related("category")
    serializer_class = serializers.ContentSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.select_related("content")
    serializer_class = serializers.BoardSerializer

    @action(detail=True, methods=["GET"])
    def top_unique_submissions(self, request, pk=None):
        board = self.get_object()
        return Response(
            RecordSubmissionSerializer(board.top_unique_submissions(), many=True).data
        )


class SettingsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    The Discord bot sets the submission webhook URLs on startup. Every other setting is edited in the admin.
    """

    API_WRITABLE_KEYS = {
        "UM_ACHIEVEMENT_SUBMISSIONS_DISCORD_WEBHOOK_URL",
        "UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL",
        "UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL",
    }

    queryset = models.Settings.objects.all()
    serializer_class = serializers.SettingsSerializer
    filterset_fields = ["key"]
    http_method_names = ["get", "patch", "head", "options"]

    def perform_update(self, serializer):
        if serializer.instance.key not in self.API_WRITABLE_KEYS:
            raise PermissionDenied(
                f"{serializer.instance.key} can only be changed in the admin."
            )
        serializer.save()
