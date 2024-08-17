from rest_framework import viewsets

from account import models
from account.api import serializers


class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer


class UserCreationSubmissionSerializer(viewsets.ModelViewSet):
    queryset = models.UserCreationSubmission.objects.all()
    serializer_class = serializers.UserCreationSubmissionSerializer
