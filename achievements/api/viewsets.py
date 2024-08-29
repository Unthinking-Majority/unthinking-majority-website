from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from achievements import models
from achievements.api import serializers
from bounty.models import Bounty


class BaseSubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.BaseSubmission.objects.all()
    serializer_class = serializers.BaseSubmissionSerializer


class RecordSubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.RecordSubmission.objects.select_related("board").prefetch_related(
        "accounts"
    )
    serializer_class = serializers.RecordSubmissionSerializer

    @action(detail=True, methods=["GET"])
    def in_active_bounty(self, request, pk=None):
        bounty = Bounty.get_current_bounty()
        if bounty and bounty.board == self.get_object().board:
            return Response({"in_active_bounty": True})
        return Response({"in_active_bounty": False})
