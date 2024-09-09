from datetime import datetime

from factory import Faker, SubFactory, django

from publications.models import Publication, PublicationComment

__all__ = (
    "PublicationFactory",
    "PublicationCommentFactory",
)


class PublicationFactory(django.DjangoModelFactory):
    author = SubFactory("users.tests.factories.UserFactory")
    title = Faker("sentence", nb_words=7)
    content = Faker("paragraph", nb_sentences=7)

    class Meta:
        model = Publication

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        pub = super()._create(model_class, *args, **kwargs)

        if kwargs.get("created"):
            pub.created = (
                kwargs["created"]
                if isinstance(kwargs["created"], datetime)
                else datetime.strptime(kwargs["created"], "%Y-%m-%d")
            )
            pub.save(update_fields=["created"])  # allow create a Publication with a specific "created" datetime

        return pub


class PublicationCommentFactory(django.DjangoModelFactory):
    author = SubFactory("users.factories.UserFactory")
    publication = SubFactory(PublicationFactory)
    content = Faker("sentence", nb_words=16)

    class Meta:
        model = PublicationComment
