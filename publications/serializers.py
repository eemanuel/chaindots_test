from rest_framework.serializers import JSONField, ModelSerializer

from publications.models import Publication, PublicationComment

__all__ = (
    "PublicationCreateSerializer",
    "PublicationSerializer",
    "PublicationCommentSerializer",
)


class PublicationSerializer(ModelSerializer):
    content = JSONField()

    class Meta:
        model = Publication
        fields = "__all__"


class PublicationCreateSerializer(ModelSerializer):
    content = JSONField()

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["author"] = obj.author.id
        return data

    class Meta:
        model = Publication
        fields = ("title", "content")


class PublicationCommentCreateSerializer(ModelSerializer):
    content = JSONField()

    class Meta:
        model = PublicationComment
        fields = ("content", "publication")

    def create(self, validated_data):
        validated_data["author"] = self.context["author"]
        return super().create(validated_data)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["author"] = obj.author.id
        return data


class PublicationCommentSerializer(ModelSerializer):
    content = JSONField()

    class Meta:
        model = PublicationComment
        fields = "__all__"
