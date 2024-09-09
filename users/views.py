from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet

from users.filters import UserFilter
from users.models import User
from users.serializers import UserDetailSerializer, UserSerializer

__all__ = ("UserCustomViewSet",)


class UserCustomViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.action == "create":
            return (AllowAny(),)
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "list"):
            return UserSerializer
        if self.action == "retrieve":
            return UserDetailSerializer

    def get_queryset(self):
        if self.action == "list":
            return User.objects.all()
        if self.action == "retrieve":
            return User.objects.all().prefetch_related("followers", "following")

    @action(detail=True, methods=["post"], url_path="follow/(?P<followed_pk>[^/.]+)")
    def follow(self, request, pk, followed_pk):
        user = self.get_object()

        try:
            user.following.add(followed_pk)
        except IntegrityError:
            return Response({"error": f"User with id={followed_pk} does not exist."}, status=HTTP_404_NOT_FOUND)

        return Response(
            {"message": f"User with id={user.pk} is now following User with id={followed_pk}."}, status=HTTP_200_OK
        )
