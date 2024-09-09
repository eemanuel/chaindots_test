from django.db.models import CASCADE, CharField, ForeignKey, TextField

from utils.models import TimeStampModel

__all__ = (
    "Publication",
    "PublicationComment",
)


class Publication(TimeStampModel):
    author = ForeignKey("users.User", on_delete=CASCADE, related_name="publications")
    title = CharField(max_length=200, blank=False, null=False)
    # "max_length" in a "TextField" is used to validate Forms but not as constraint in the DB
    content = TextField(max_length=5_000, blank=False, null=False)


class PublicationComment(TimeStampModel):
    author = ForeignKey("users.User", on_delete=CASCADE, related_name="comments")
    publication = ForeignKey("publications.Publication", on_delete=CASCADE, related_name="comments")
    # "max_length" in a "TextField" is used to validate Forms but not as constraint in the DB
    content = TextField(max_length=2_000, blank=False, null=False)
