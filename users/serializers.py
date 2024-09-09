from django.contrib.auth.hashers import make_password

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import User

__all__ = (
    "UserSerializer",
    "UserDetailSerializer",
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ("following",)
        extra_kwargs = {
            "password": {"write_only": True},
            "is_active": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "publications_count": {"read_only": True},
            "comments_count": {"read_only": True},
        }

    def create(self, validated_data):
        # "make_password" is to encrypt the password in postgres
        validated_data["password"] = make_password(validated_data["password"])
        user = super().create(validated_data)
        return user


class UserDetailSerializer(UserSerializer):
    following = SerializerMethodField(required=False, read_only=True)
    followers = SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def get_following(self, user):
        return user.following.values_list("id", flat=True)

    def get_followers(self, user):
        return user.followers.values_list("id", flat=True)
