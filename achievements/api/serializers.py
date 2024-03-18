from rest_framework import serializers

from achievements import models
from main.api.serializers import BoardSerializer
from account.api.serializers import AccountSerializer


class BaseSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseSubmission
        fields = ["pk", "proof", "notes", "denial_notes", "accepted", "date"]


class RecordSubmissionSerializer(BaseSubmissionSerializer):
    accounts = AccountSerializer(many=True)
    board = BoardSerializer()

    class Meta(BaseSubmissionSerializer.Meta):
        model = models.RecordSubmission
        fields = BaseSubmissionSerializer.Meta.fields + ["accounts", "board", "value"]
