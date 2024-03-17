from rest_framework import serializers

from main.models import Board, Content, ContentCategory


class ContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentCategory
        fields = ["pk", "name", "slug"]


class ContentSerializer(serializers.ModelSerializer):
    category = ContentCategorySerializer()
    difficulty = serializers.SerializerMethodField()
    metric = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            "pk",
            "name",
            "hiscores_name",
            "category",
            "difficulty",
            "has_pbs",
            "has_hiscores",
            "can_be_mentored",
            "can_be_split",
            "metric",
            "metric_name",
            "slug",
            "icon",
            "ordering",
            "order",
        ]

    def get_difficulty(self, obj):
        return obj.get_difficulty_display()

    def get_metric(self, obj):
        return obj.get_metric_display()


class BoardSerializer(serializers.ModelSerializer):
    content = ContentSerializer()

    class Meta:
        model = Board
        fields = [
            "pk",
            "name",
            "content",
            "team_size",
            "points_multiplier",
            "is_active",
        ]
