from django_filters.rest_framework import CharFilter, DateTimeFilter, FilterSet

from publications.models import Publication

__all__ = ("PublicationFilter",)


class PublicationFilter(FilterSet):
    author = CharFilter(field_name="author__id")
    from_date = DateTimeFilter(field_name="created", lookup_expr="gte", input_formats=["%d-%m-%Y"])
    to_date = DateTimeFilter(field_name="created", lookup_expr="lte", input_formats=["%d-%m-%Y"])

    class Meta:
        model = Publication
        fields = ["author", "from_date", "to_date"]
