from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from account import models
from account.api import serializers


class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    filterset_fields = ["discord_id"]


class UserCreationSubmissionSerializer(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    queryset = models.UserCreationSubmission.objects.all()
    serializer_class = serializers.UserCreationSubmissionSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise ValidationError(e.messages)
