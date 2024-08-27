from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from account import models


class AccountSerializer(serializers.ModelSerializer):
    admin_url = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = models.Account
        fields = [
            "pk",
            "admin_url",
            "discord_id",
            "name",
            "preferred_name",
            "is_active",
            "rank",
        ]

    def get_admin_url(self, obj):
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            kwargs={"object_id": obj.pk},
        )
        if settings.DEBUG:
            protocol = "https://"
        else:
            protocol = "http://"
        return f"{protocol}{settings.DOMAIN}{url}"

    def get_rank(self, obj):
        return obj.get_rank_display()


class UserCreationSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserCreationSubmission
        fields = "__all__"
