from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from dragonstone import models


class DragonstoneBaseSubmissionSerializer(serializers.ModelSerializer):
    admin_url = serializers.SerializerMethodField()

    class Meta:
        model = models.DragonstoneBaseSubmission
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
            protocol = "http://"
        else:
            protocol = "https://"
        return f"{protocol}{settings.DOMAIN}{url}"
