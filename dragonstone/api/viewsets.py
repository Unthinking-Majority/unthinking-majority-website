from rest_framework import viewsets

from dragonstone import models
from dragonstone.api import serializers


class DragonstoneBaseSubmissionViewSet(viewsets.ModelViewSet):
    queryset = models.DragonstoneBaseSubmission.objects.all()
    serializer_class = serializers.DragonstoneBaseSubmissionSerializer
