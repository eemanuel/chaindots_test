from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from publications.filters import PublicationFilter
from publications.models import Publication, PublicationComment
from publications.serializers import (
    PublicationCommentCreateSerializer,
    PublicationCommentSerializer,
    PublicationCreateSerializer,
    PublicationSerializer,
)
from users.serializers import UserSerializer

__all__ = ("PublicationModelViewSet",)


class PublicationModelViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    filterset_class = PublicationFilter

    def get_serializer_class(self):
        if self.action == "create":
            return PublicationCreateSerializer
        if self.action == "list":
            return PublicationSerializer
        if self.action == ("comments"):
            return PublicationCommentSerializer

    def get_queryset(self):
        if self.action in ("retrieve", "create"):
            return Publication.objects.select_related("author")
        if self.action == "list":
            return Publication.objects.order_by("-created")
        if self.action == "comments":
            return Publication.objects.all()

    def retrieve(self, request, *args, **kwargs):
        publication = self.get_object()

        last_3_comments = PublicationComment.objects.raw(
            f"SELECT * FROM publications_publicationcomment "
            f"WHERE publication_id = {publication.id} ORDER BY id DESC LIMIT 3;"
        )

        data = {
            "publication": PublicationSerializer(publication).data,
            "last_3_comments": PublicationCommentSerializer(last_3_comments, many=True).data,
            "author": UserSerializer(publication.author).data,
        }

        return Response(data)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        if request.method == "POST":
            return self._comments_post(request, pk)
        if request.method == "GET":
            return self._comments_get(pk)

    def _comments_post(self, request, publication_id):
        serializer = PublicationCommentCreateSerializer(
            data=request.data | {"publication": publication_id}, context={"author": request.user}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _comments_get(self, publication_id):
        queryset = (
            PublicationComment.objects.filter(publication=publication_id).select_related("author").order_by("-created")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PublicationCommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicationCommentSerializer(queryset, many=True)
        return Response(serializer.data)
