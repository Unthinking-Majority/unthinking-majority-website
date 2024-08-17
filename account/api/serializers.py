from rest_framework import serializers

from account import models


class AccountSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = models.Account
        fields = ["pk", "name", "preferred_name", "is_active", "rank"]

    def get_rank(self, obj):
        return obj.get_rank_display()


class UserCreationSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserCreationSubmission
        fields = "__all__"
