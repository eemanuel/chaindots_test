from django_filters.rest_framework import CharFilter, FilterSet

from users.models import User

__all__ = ("UserFilter",)


class UserFilter(FilterSet):
    username = CharFilter(field_name="username", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["username"]
