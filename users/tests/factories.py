from django.contrib.auth import get_user_model

from factory import Faker, PostGenerationMethodCall, django

__all__ = ("UserFactory",)


User = get_user_model()


class UserFactory(django.DjangoModelFactory):
    username = Faker("user_name")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    password = PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User
