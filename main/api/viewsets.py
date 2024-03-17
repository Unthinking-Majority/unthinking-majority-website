from rest_framework import viewsets

from main import models
from main.api import serializers


class ContentCateogryViewSet(viewsets.ModelViewSet):
    queryset = models.ContentCategory.objects.all()
    serializer_class = serializers.ContentCategorySerializer


class ContentViewSet(viewsets.ModelViewSet):
    queryset = models.Content.objects.select_related("category")
    serializer_class = serializers.ContentSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.select_related("content")
    serializer_class = serializers.BoardSerializer
