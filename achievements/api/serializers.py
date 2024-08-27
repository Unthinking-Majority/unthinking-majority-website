from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from account.api.serializers import AccountSerializer
from achievements import models
from main.api.serializers import BoardSerializer


class BaseSubmissionSerializer(serializers.ModelSerializer):
    admin_url = serializers.SerializerMethodField()

    class Meta:
        model = models.BaseSubmission
        fields = [
            "pk",
            "proof",
            "notes",
            "denial_notes",
            "accepted",
            "date",
            "admin_url",
        ]

    def get_admin_url(self, obj):
        instance = obj.get_real_instance()
        url = reverse(
            f"admin:{instance._meta.app_label}_{instance._meta.model_name}_change",
            kwargs={"object_id": instance.pk},
        )
        if settings.DEBUG:
            protocol = "https://"
        else:
            protocol = "http://"
        return f"{protocol}{settings.DOMAIN}{url}"


class RecordSubmissionSerializer(BaseSubmissionSerializer):
    accounts = AccountSerializer(many=True)
    board = BoardSerializer()

    class Meta(BaseSubmissionSerializer.Meta):
        model = models.RecordSubmission
        fields = BaseSubmissionSerializer.Meta.fields + ["accounts", "board", "value"]
