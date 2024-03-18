from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=True, methods=["GET"])
    def get_top_unique_submissions(self, request, pk=None):
        board = self.get_object()
        return Response(board)
