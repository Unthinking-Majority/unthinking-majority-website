from rest_framework import viewsets

from achievements import models
from achievements.api import serializers


class BaseSubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.BaseSubmission.objects.all()
    serializer_class = serializers.BaseSubmissionSerializer


class RecordSubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.RecordSubmission.objects.select_related("board").prefetch_related(
        "accounts"
    )
    serializer_class = serializers.RecordSubmissionSerializer
